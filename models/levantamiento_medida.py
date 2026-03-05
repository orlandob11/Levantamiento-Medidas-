# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class LevantamientoMedida(models.Model):
    _name = 'levantamiento.medida'
    _description = 'Levantamiento de Medidas'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha desc, name desc'

    name = fields.Char(
        string='Referencia',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Nuevo'),
        tracking=True,
    )

    # Relación con cliente y sucursal
    cliente_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True,
        tracking=True,
        domain="[('is_company', '=', True), ('parent_id', '=', False)]",
        help='Seleccione el cliente (empresa matriz)',
    )
    sucursal_id = fields.Many2one(
        'res.partner',
        string='Sucursal',
        tracking=True,
        domain="[('parent_id', '=', cliente_id)]",
        help='Seleccione la sucursal del cliente (opcional si el cliente no tiene sucursales)',
    )

    # Dirección para mostrar en formulario
    direccion_trabajo = fields.Char(
        string='Dirección del Trabajo',
        compute='_compute_direccion_trabajo',
        store=True,
    )

    # Fechas
    fecha = fields.Date(
        string='Fecha del Levantamiento',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    fecha_instalacion = fields.Date(
        string='Fecha de Instalación',
        tracking=True,
    )

    # Responsables
    responsable_id = fields.Many2one(
        'res.users',
        string='Responsable',
        default=lambda self: self.env.user,
        tracking=True,
    )
    instalador_id = fields.Many2one(
        'res.users',
        string='Instalador',
        tracking=True,
    )

    # Estado
    state = fields.Selection([
        ('borrador', 'Borrador'),
        ('medido', 'Medido'),
        ('en_produccion', 'En Producción'),
        ('en_instalacion', 'En Instalación'),
        ('instalado', 'Instalado'),
        ('cerrado', 'Cerrado'),
        ('cancelado', 'Cancelado'),
    ], string='Estado', default='borrador', required=True, tracking=True, copy=False)

    # Líneas de medidas
    linea_ids = fields.One2many(
        'levantamiento.linea',
        'levantamiento_id',
        string='Líneas de Medidas',
        copy=True,
    )
    linea_count = fields.Integer(
        string='Nº de Elementos',
        compute='_compute_linea_count',
    )
    evento_ids = fields.One2many(
        'levantamiento.linea.log',
        'levantamiento_id',
        string='Eventos Compartidos',
        copy=True,
    )

    # Fotos/Adjuntos del Chatter
    attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Adjuntos',
        compute='_compute_attachment_ids',
    )
    image_ids = fields.Many2many(
        'ir.attachment',
        string='Fotos',
        compute='_compute_attachment_ids',
    )
    attachment_count = fields.Integer(
        string='Nº de Adjuntos',
        compute='_compute_attachment_ids',
    )

    # Notas
    notas_levantamiento = fields.Html(
        string='Notas del Levantamiento',
    )
    notas_instalacion = fields.Html(
        string='Notas de Instalación',
    )
    incidencias = fields.Html(
        string='Incidencias',
        help='Registre aquí los problemas encontrados durante la instalación',
    )

    # Campos de auditoría adicionales
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        default=lambda self: self.env.company,
        required=True,
    )

    # Colores para kanban
    color = fields.Integer(string='Color')
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Baja'),
        ('2', 'Alta'),
        ('3', 'Muy Alta'),
    ], string='Prioridad', default='0')

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------

    @api.depends('cliente_id', 'sucursal_id')
    def _compute_direccion_trabajo(self):
        for record in self:
            partner = record.sucursal_id or record.cliente_id
            if partner:
                direccion_parts = []
                if partner.street:
                    direccion_parts.append(partner.street)
                if partner.street2:
                    direccion_parts.append(partner.street2)
                if partner.city:
                    direccion_parts.append(partner.city)
                if partner.state_id:
                    direccion_parts.append(partner.state_id.name)
                if partner.country_id:
                    direccion_parts.append(partner.country_id.name)
                record.direccion_trabajo = ', '.join(direccion_parts)
            else:
                record.direccion_trabajo = False

    @api.depends('linea_ids')
    def _compute_linea_count(self):
        for record in self:
            record.linea_count = len(record.linea_ids)

    def _compute_attachment_ids(self):
        """Obtener adjuntos e imágenes del chatter"""
        for record in self:
            attachments = self.env['ir.attachment'].search([
                ('res_model', '=', 'levantamiento.medida'),
                ('res_id', '=', record.id),
            ])
            record.attachment_ids = attachments
            # Filtrar solo imágenes
            record.image_ids = attachments.filtered(
                lambda a: a.mimetype and a.mimetype.startswith('image/')
            )
            record.attachment_count = len(attachments)

    # -------------------------------------------------------------------------
    # ONCHANGE METHODS
    # -------------------------------------------------------------------------

    @api.onchange('cliente_id')
    def _onchange_cliente_id(self):
        """Limpiar sucursal cuando cambia el cliente"""
        self.sucursal_id = False

    # -------------------------------------------------------------------------
    # CRUD METHODS
    # -------------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nuevo')) == _('Nuevo'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'levantamiento.medida'
                ) or _('Nuevo')
        return super().create(vals_list)

    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'name': _('Nuevo'),
            'state': 'borrador',
            'fecha': fields.Date.context_today(self),
            'fecha_instalacion': False,
        })
        return super().copy(default)

    # -------------------------------------------------------------------------
    # ACTION METHODS
    # -------------------------------------------------------------------------

    def action_confirmar_medidas(self):
        """Confirmar que las medidas han sido tomadas"""
        for record in self:
            if not record.linea_ids:
                raise ValidationError(_('Debe agregar al menos una línea de medidas antes de confirmar.'))
            record.state = 'medido'

    def action_enviar_produccion(self):
        """Enviar a producción"""
        self.write({'state': 'en_produccion'})

    def action_iniciar_instalacion(self):
        """Iniciar instalación"""
        self.write({'state': 'en_instalacion'})

    def action_marcar_instalado(self):
        """Marcar como instalado"""
        self.write({
            'state': 'instalado',
            'fecha_instalacion': fields.Date.context_today(self),
        })

    def action_cerrar(self):
        """Cerrar el levantamiento"""
        self.write({'state': 'cerrado'})

    def action_cancelar(self):
        """Cancelar el levantamiento"""
        self.write({'state': 'cancelado'})

    def action_restablecer_borrador(self):
        """Volver a borrador"""
        self.write({'state': 'borrador'})

    def action_add_linea_fullscreen(self):
        """Crear línea de medida en pantalla completa"""
        self.ensure_one()
        return {
            'name': _('Nueva Línea de Medida'),
            'type': 'ir.actions.act_window',
            'res_model': 'levantamiento.linea',
            'view_mode': 'form',
            'view_id': self.env.ref('levantamiento_medidas.view_levantamiento_linea_form_detail').id,
            'target': 'current',
            'context': {
                'default_levantamiento_id': self.id,
            },
        }

    def action_add_evento_compartido(self):
        """Crear evento compartido para múltiples elementos"""
        self.ensure_one()
        return {
            'name': _('Nuevo Evento Compartido'),
            'type': 'ir.actions.act_window',
            'res_model': 'levantamiento.linea.log',
            'view_mode': 'form',
            'view_id': self.env.ref('levantamiento_medidas.view_levantamiento_linea_log_form').id,
            'target': 'current',
            'context': {
                'default_levantamiento_id': self.id,
            },
        }

    def action_ver_adjuntos(self):
        """Abrir adjuntos del chatter"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Adjuntos'),
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,tree,form',
            'domain': [
                ('res_model', '=', 'levantamiento.medida'),
                ('res_id', '=', self.id),
            ],
            'context': {
                'default_res_model': 'levantamiento.medida',
                'default_res_id': self.id,
            },
        }

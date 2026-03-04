# -*- coding: utf-8 -*-

from odoo import models, fields, api


class LevantamientoLineaLog(models.Model):
    _name = 'levantamiento.linea.log'
    _description = 'Historial de Línea de Medidas'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha desc, id desc'
    _rec_name = 'resumen'

    # -------------------------------------------------------------------------
    # FIELDS
    # -------------------------------------------------------------------------

    linea_id = fields.Many2one(
        'levantamiento.linea',
        string='Línea de Medidas',
        required=True,
        ondelete='cascade',
        index=True,
    )

    # Tipo de evento
    tipo = fields.Selection([
        ('incidencia', 'Incidencia'),
        ('reparacion', 'Reparación'),
        ('instalacion', 'Instalación'),
        ('cambio_medida', 'Cambio de Medidas'),
        ('ajuste', 'Ajuste'),
        ('inspeccion', 'Inspección'),
        ('mantenimiento', 'Mantenimiento'),
        ('otro', 'Otro'),
    ], string='Tipo de Evento', required=True, default='incidencia')

    # Datos del evento
    fecha = fields.Datetime(
        string='Fecha y Hora',
        default=fields.Datetime.now,
        required=True,
    )
    usuario_id = fields.Many2one(
        'res.users',
        string='Registrado por',
        default=lambda self: self.env.user,
        required=True,
    )
    resumen = fields.Char(
        string='Resumen',
        required=True,
        help='Breve descripción del evento',
    )
    descripcion = fields.Html(
        string='Descripción Detallada',
    )

    # Campos para cambio de medidas
    medida_anterior = fields.Char(
        string='Medida Anterior',
        help='Registrar la medida anterior si hubo cambio',
    )
    medida_nueva = fields.Char(
        string='Medida Nueva',
        help='Registrar la nueva medida',
    )

    # Estado/Resultado
    estado = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('resuelto', 'Resuelto'),
        ('no_resuelto', 'No Resuelto'),
    ], string='Estado', default='pendiente')

    # Costo asociado (opcional)
    costo = fields.Float(
        string='Costo',
        digits=(10, 2),
        help='Costo asociado a esta incidencia/reparación',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id,
    )

    # Líneas de costos
    costo_ids = fields.One2many(
        'levantamiento.evento.costo',
        'log_id',
        string='Costos',
    )
    costo_total = fields.Float(
        string='Costo Total',
        compute='_compute_costo_total',
        store=True,
        digits=(10, 2),
    )

    # Fotos del evento
    image_1 = fields.Image(
        string='Foto 1',
        max_width=1920,
        max_height=1920,
    )
    image_2 = fields.Image(
        string='Foto 2',
        max_width=1920,
        max_height=1920,
    )

    # -------------------------------------------------------------------------
    # COMPUTE / DISPLAY
    # -------------------------------------------------------------------------

    @api.depends('costo_ids.subtotal')
    def _compute_costo_total(self):
        for record in self:
            record.costo_total = sum(record.costo_ids.mapped('subtotal'))

    def action_open_form(self):
        """Abrir evento en pantalla completa para mostrar chatter"""
        self.ensure_one()
        return {
            'name': self.display_name,
            'type': 'ir.actions.act_window',
            'res_model': 'levantamiento.linea.log',
            'view_mode': 'form',
            'view_id': self.env.ref('levantamiento_medidas.view_levantamiento_linea_log_form').id,
            'res_id': self.id,
            'target': 'current',
        }

    def name_get(self):
        result = []
        for record in self:
            tipo_label = dict(self._fields['tipo'].selection).get(record.tipo, '')
            name = f"[{tipo_label}] {record.resumen}"
            result.append((record.id, name))
        return result

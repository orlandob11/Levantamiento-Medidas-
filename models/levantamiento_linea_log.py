# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class LevantamientoLineaLog(models.Model):
    _name = 'levantamiento.linea.log'
    _description = 'Historial de Eventos de Elementos'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha desc, id desc'
    _rec_name = 'resumen'

    # -------------------------------------------------------------------------
    # FIELDS
    # -------------------------------------------------------------------------

    linea_id = fields.Many2one(
        'levantamiento.linea',
        string='Elemento (legado)',
        ondelete='cascade',
        index=True,
        help='Campo legado para compatibilidad con eventos anteriores.',
    )
    levantamiento_id = fields.Many2one(
        'levantamiento.medida',
        string='Levantamiento',
        index=True,
    )
    linea_ids = fields.Many2many(
        'levantamiento.linea',
        'levantamiento_linea_log_rel',
        'log_id',
        'linea_id',
        string='Elementos Relacionados',
        required=True,
    )

    # Tipo de evento
    tipo = fields.Selection([
        ('incidencia', 'Incidencia'),
        ('reparacion', 'Reparación'),
        ('instalacion', 'Instalación'),
        ('cambio_medida', 'Cambio de Dimensiones'),
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
        string='Dimensión Anterior',
        help='Registrar la medida anterior si hubo cambio',
    )
    medida_nueva = fields.Char(
        string='Dimensión Nueva',
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

    def init(self):
        """Migrar eventos antiguos (linea_id) a la relación múltiple (linea_ids)."""
        self.env.cr.execute("""
            INSERT INTO levantamiento_linea_log_rel (log_id, linea_id)
            SELECT l.id, l.linea_id
            FROM levantamiento_linea_log l
            WHERE l.linea_id IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1
                  FROM levantamiento_linea_log_rel r
                  WHERE r.log_id = l.id AND r.linea_id = l.linea_id
              )
        """)

    @api.depends('costo_ids.subtotal')
    def _compute_costo_total(self):
        for record in self:
            record.costo_total = sum(record.costo_ids.mapped('subtotal'))

    @api.onchange('linea_ids')
    def _onchange_linea_ids(self):
        for record in self:
            record.linea_id = False
            if record.linea_ids:
                record.levantamiento_id = record.linea_ids[0].levantamiento_id

    @api.onchange('levantamiento_id')
    def _onchange_levantamiento_id(self):
        for record in self:
            if record.levantamiento_id:
                record.linea_ids = record.linea_ids.filtered(
                    lambda linea: linea.levantamiento_id == record.levantamiento_id
                )

    @api.constrains('linea_ids', 'levantamiento_id')
    def _check_event_targets(self):
        for record in self:
            lineas = record.linea_ids
            if not lineas:
                raise ValidationError(_('Debe seleccionar al menos un elemento para registrar el evento.'))

            levantamientos = lineas.mapped('levantamiento_id')
            if len(levantamientos) > 1:
                raise ValidationError(_('Los elementos seleccionados deben pertenecer al mismo levantamiento.'))

            if record.levantamiento_id and levantamientos and record.levantamiento_id != levantamientos[0]:
                raise ValidationError(_('El levantamiento del evento no coincide con los elementos seleccionados.'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            linea_id = vals.get('linea_id')
            if linea_id and not vals.get('linea_ids'):
                vals['linea_ids'] = [(6, 0, [linea_id])]
        records = super().create(vals_list)
        for record in records.filtered(lambda rec: rec.linea_ids and not rec.levantamiento_id):
            record.levantamiento_id = record.linea_ids[0].levantamiento_id
        return records

    def write(self, vals):
        vals = dict(vals)
        if vals.get('linea_id') and 'linea_ids' not in vals:
            vals['linea_ids'] = [(4, vals['linea_id'])]
        res = super().write(vals)
        for record in self.filtered(lambda rec: rec.linea_ids and not rec.levantamiento_id):
            record.levantamiento_id = record.linea_ids[0].levantamiento_id
        return res

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

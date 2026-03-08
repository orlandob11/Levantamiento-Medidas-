# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class LevantamientoLinea(models.Model):
    _name = 'levantamiento.linea'
    _description = 'Elemento del Levantamiento'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id'
    _rec_name = 'name'

    levantamiento_id = fields.Many2one(
        'levantamiento.medida',
        string='Levantamiento',
        required=True,
        ondelete='cascade',
        index=True,
    )

    sequence = fields.Integer(
        string='Secuencia',
        default=10,
    )
    name = fields.Char(
        string='Nombre',
        compute='_compute_name',
        store=True,
    )

    # Tipo de elemento (configurable)
    tipo_elemento_id = fields.Many2one(
        'levantamiento.tipo.elemento',
        string='Tipo de Elemento',
        required=True,
    )

    # Ubicación del elemento
    ubicacion = fields.Char(
        string='Ubicación',
        help='Ej: Entrada principal, Vitrina izquierda, Techo recepción',
    )

    # Medidas con UoM
    ancho = fields.Float(
        string='Ancho',
        digits=(10, 2),
    )
    alto = fields.Float(
        string='Alto',
        digits=(10, 2),
    )
    profundidad = fields.Float(
        string='Profundidad',
        digits=(10, 2),
        help='Dejar en 0 si no aplica',
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unidad de Medida',
        default=lambda self: self.env.ref('uom.product_uom_cm', raise_if_not_found=False),
        domain=lambda self: [('category_id', '=', self.env.ref('uom.uom_categ_length', raise_if_not_found=False).id if self.env.ref('uom.uom_categ_length', raise_if_not_found=False) else False)],
        required=True,
    )
    conversion_uom_id = fields.Many2one(
        'uom.uom',
        string='Convertir a',
        default=lambda self: self.env.ref('uom.product_uom_meter', raise_if_not_found=False),
        domain=lambda self: [('category_id', '=', self.env.ref('uom.uom_categ_length', raise_if_not_found=False).id if self.env.ref('uom.uom_categ_length', raise_if_not_found=False) else False)],
        help='Unidad objetivo para visualizar la conversión de dimensiones',
    )

    # Campos calculados para conversiones
    ancho_m = fields.Float(
        string='Ancho (convertido)',
        compute='_compute_medidas_convertidas',
        digits=(10, 4),
        store=True,
    )
    alto_m = fields.Float(
        string='Alto (convertido)',
        compute='_compute_medidas_convertidas',
        digits=(10, 4),
        store=True,
    )
    profundidad_m = fields.Float(
        string='Profundidad (convertido)',
        compute='_compute_medidas_convertidas',
        digits=(10, 4),
        store=True,
    )
    area_ft2 = fields.Float(
        string='Área (ft²)',
        compute='_compute_area',
        digits=(10, 2),
        store=True,
        help='Área calculada: Ancho x Alto en pies cuadrados',
    )

    # Cantidad (para elementos repetidos)
    cantidad = fields.Integer(
        string='Cantidad',
        default=1,
    )
    area_total_ft2 = fields.Float(
        string='Área Total (ft²)',
        compute='_compute_area',
        digits=(10, 2),
        store=True,
        help='Área total: Área x Cantidad',
    )

    # Foto del elemento
    image_1920 = fields.Image(
        string='Foto',
        max_width=1920,
        max_height=1920,
    )
    image_128 = fields.Image(
        string='Miniatura',
        related='image_1920',
        max_width=128,
        max_height=128,
        store=True,
    )

    # Notas
    notas = fields.Text(
        string='Notas',
    )

    # Historial de eventos
    log_ids = fields.One2many(
        'levantamiento.linea.log',
        'linea_id',
        string='Historial de Eventos',
    )
    log_event_ids = fields.Many2many(
        'levantamiento.linea.log',
        string='Eventos Relacionados',
        compute='_compute_log_event_data',
    )
    log_count = fields.Integer(
        string='Eventos',
        compute='_compute_log_event_data',
    )

    # Estado de la línea
    estado_linea = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('instalado', 'Instalado'),
        ('con_incidencia', 'Con Incidencia'),
        ('resuelto', 'Resuelto'),
    ], string='Estado', default='pendiente', tracking=True)

    # Campos relacionados para vistas
    cliente_id = fields.Many2one(
        related='levantamiento_id.cliente_id',
        store=True,
        string='Cliente',
    )
    fecha = fields.Date(
        related='levantamiento_id.fecha',
        store=True,
        string='Fecha',
    )

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------

    @api.depends('ancho', 'alto', 'profundidad', 'uom_id', 'conversion_uom_id')
    def _compute_medidas_convertidas(self):
        """Convertir dimensiones a la unidad seleccionada"""
        uom_m = self.env.ref('uom.product_uom_meter', raise_if_not_found=False)
        for record in self:
            target_uom = record.conversion_uom_id or uom_m
            if (
                record.uom_id
                and target_uom
                and record.uom_id.category_id == target_uom.category_id
            ):
                record.ancho_m = record.uom_id._compute_quantity(
                    record.ancho, target_uom, round=False
                )
                record.alto_m = record.uom_id._compute_quantity(
                    record.alto, target_uom, round=False
                )
                record.profundidad_m = record.uom_id._compute_quantity(
                    record.profundidad, target_uom, round=False
                )
            else:
                record.ancho_m = 0
                record.alto_m = 0
                record.profundidad_m = 0

    @api.depends('ancho', 'alto', 'cantidad', 'uom_id')
    def _compute_area(self):
        """Calcular área en ft² (pies cuadrados) - conversión directa a pies"""
        uom_foot = self.env.ref('uom.product_uom_foot', raise_if_not_found=False)
        for record in self:
            if record.uom_id and uom_foot:
                try:
                    # Convertir directamente a pies para evitar errores de redondeo
                    ancho_ft = record.uom_id._compute_quantity(
                        record.ancho, uom_foot, round=False
                    )
                    alto_ft = record.uom_id._compute_quantity(
                        record.alto, uom_foot, round=False
                    )
                    # Calcular área y redondear a 2 decimales
                    record.area_ft2 = round(ancho_ft * alto_ft, 2)
                    record.area_total_ft2 = round(record.area_ft2 * (record.cantidad or 1), 2)
                except Exception:
                    record.area_ft2 = 0
                    record.area_total_ft2 = 0
            else:
                record.area_ft2 = 0
                record.area_total_ft2 = 0

    @api.depends('tipo_elemento_id.name', 'ubicacion', 'ancho', 'alto', 'uom_id.name')
    def _compute_name(self):
        for record in self:
            name = f"{record.tipo_elemento_id.name or _('Elemento')}"
            if record.ubicacion:
                name += f" - {record.ubicacion}"
            if record.ancho and record.alto:
                name += f" ({record.ancho} x {record.alto} {record.uom_id.name or ''})"
            record.name = name

    def _compute_log_event_data(self):
        log_model = self.env['levantamiento.linea.log']
        for record in self:
            logs = log_model.search([('linea_ids', 'in', record.id)], order='fecha desc')
            record.log_event_ids = logs
            record.log_count = len(logs)

    # -------------------------------------------------------------------------
    # ACTIONS
    # -------------------------------------------------------------------------

    def action_view_logs(self):
        """Ver historial de eventos de esta línea"""
        self.ensure_one()
        return {
            'name': f'Historial: {self.tipo_elemento_id.name or "Elemento"}',
            'type': 'ir.actions.act_window',
            'res_model': 'levantamiento.linea.log',
            'view_mode': 'tree,form',
            'domain': [('linea_ids', 'in', self.id)],
            'context': {
                'default_linea_ids': [(6, 0, [self.id])],
                'default_levantamiento_id': self.levantamiento_id.id,
            },
        }

    def action_open_detail(self):
        """Abrir detalle en pantalla completa para mostrar chatter"""
        self.ensure_one()
        return {
            'name': self.display_name,
            'type': 'ir.actions.act_window',
            'res_model': 'levantamiento.linea',
            'view_mode': 'form',
            'view_id': self.env.ref('levantamiento_medidas.view_levantamiento_linea_form_detail').id,
            'res_id': self.id,
            'target': 'current',
        }

    def action_add_log(self):
        """Agregar nuevo evento al historial"""
        self.ensure_one()
        return {
            'name': 'Registrar Evento',
            'type': 'ir.actions.act_window',
            'res_model': 'levantamiento.linea.log',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_linea_ids': [(6, 0, [self.id])],
                'default_levantamiento_id': self.levantamiento_id.id,
            },
        }

    # -------------------------------------------------------------------------
    # DISPLAY NAME
    # -------------------------------------------------------------------------

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.name or _('Elemento')))
        return result

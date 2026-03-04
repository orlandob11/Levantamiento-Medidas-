# -*- coding: utf-8 -*-

from odoo import api, fields, models


class LevantamientoEventoCosto(models.Model):
    _name = 'levantamiento.evento.costo'
    _description = 'Costo de Evento de Línea'
    _order = 'id'

    log_id = fields.Many2one(
        'levantamiento.linea.log',
        string='Evento',
        required=True,
        ondelete='cascade',
        index=True,
    )

    descripcion = fields.Char(
        string='Descripción',
        required=True,
    )

    cantidad = fields.Float(
        string='Cantidad',
        default=1.0,
        digits=(10, 2),
    )

    precio_unitario = fields.Float(
        string='Precio Unitario',
        digits=(10, 2),
    )

    subtotal = fields.Float(
        string='Subtotal',
        compute='_compute_subtotal',
        store=True,
        digits=(10, 2),
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        related='log_id.currency_id',
        store=True,
    )

    @api.depends('cantidad', 'precio_unitario')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.cantidad * record.precio_unitario

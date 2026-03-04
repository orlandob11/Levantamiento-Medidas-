# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class LevantamientoTipoElemento(models.Model):
    _name = 'levantamiento.tipo.elemento'
    _description = 'Tipo de Elemento para Levantamiento'
    _order = 'sequence, name'

    name = fields.Char(
        string='Nombre',
        required=True,
        translate=True,
    )
    code = fields.Char(
        string='Código',
        required=True,
    )
    descripcion = fields.Text(
        string='Descripción',
        translate=True,
    )
    sequence = fields.Integer(
        string='Secuencia',
        default=10,
    )
    active = fields.Boolean(
        string='Activo',
        default=True,
    )
    color = fields.Integer(
        string='Color',
        default=0,
    )

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'El código del tipo de elemento debe ser único.'),
    ]

    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.code}] {record.name}" if record.code else record.name
            result.append((record.id, name))
        return result

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        if name:
            domain = ['|', ('code', operator, name), ('name', operator, name)] + domain
        return self._search(domain, limit=limit, order=order)

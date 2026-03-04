# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class LevantamientoFoto(models.Model):
    _name = 'levantamiento.foto'
    _description = 'Foto de Referencia del Levantamiento'
    _order = 'sequence, id'

    levantamiento_id = fields.Many2one(
        'levantamiento.medida',
        string='Levantamiento',
        required=True,
        ondelete='cascade',
        index=True,
    )

    name = fields.Char(
        string='Descripción',
        required=True,
        help='Descripción breve de la foto (ej: Vista frontal, Detalle instalación)',
    )

    sequence = fields.Integer(
        string='Secuencia',
        default=10,
    )

    # Imágenes con diferentes resoluciones
    image_1920 = fields.Image(
        string='Foto',
        max_width=1920,
        max_height=1920,
        required=True,
    )
    image_1024 = fields.Image(
        string='Foto 1024',
        related='image_1920',
        max_width=1024,
        max_height=1024,
        store=True,
    )
    image_512 = fields.Image(
        string='Foto 512',
        related='image_1920',
        max_width=512,
        max_height=512,
        store=True,
    )
    image_256 = fields.Image(
        string='Foto 256',
        related='image_1920',
        max_width=256,
        max_height=256,
        store=True,
    )
    image_128 = fields.Image(
        string='Miniatura',
        related='image_1920',
        max_width=128,
        max_height=128,
        store=True,
    )

    # Categoría de la foto
    tipo = fields.Selection([
        ('antes', 'Antes de Instalación'),
        ('durante', 'Durante Instalación'),
        ('despues', 'Después de Instalación'),
        ('problema', 'Problema/Incidencia'),
        ('referencia', 'Referencia General'),
    ], string='Tipo de Foto', default='referencia')

    # Fecha de la foto
    fecha = fields.Datetime(
        string='Fecha de la Foto',
        default=fields.Datetime.now,
    )

    # Notas
    notas = fields.Text(
        string='Notas',
    )

    # Campos relacionados para filtros
    cliente_id = fields.Many2one(
        related='levantamiento_id.cliente_id',
        store=True,
        string='Cliente',
    )
    sucursal_id = fields.Many2one(
        related='levantamiento_id.sucursal_id',
        store=True,
        string='Sucursal',
    )
    levantamiento_name = fields.Char(
        related='levantamiento_id.name',
        string='Referencia Levantamiento',
    )

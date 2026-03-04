# -*- coding: utf-8 -*-
{
    'name': 'Levantamiento de Medidas',
    'version': '17.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Gestión de levantamientos de medidas para trabajos de rotulación e instalación',
    'description': """
Levantamiento de Medidas para Odoo 17
=====================================

Este módulo permite gestionar los levantamientos de medidas en sucursales de clientes,
con seguimiento tipo CRM para instalaciones y reimpresiones futuras.

Características principales:
----------------------------
* Gestión de medidas por cliente y sucursal
* Tipos de elementos configurables (cristales, vallas, letreros, etc.)
* Soporte para unidades de medida con conversiones
* Galería de fotos de referencia
* Notas de instalación y seguimiento de incidencias
* Historial completo vía chatter
* Reportes PDF imprimibles
* Estados tipo pipeline: Borrador → Medido → En Instalación → Instalado → Cerrado
    """,
    'author': 'Tu Empresa',
    'website': 'https://www.tuempresa.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'contacts',
        'mail',
        'uom',
    ],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',
        # Data
        'data/sequence_data.xml',
        'data/tipo_elemento_data.xml',
        # Reports (must load before views that reference them)
        'report/levantamiento_report.xml',
        'report/levantamiento_template.xml',
        # Views
        'views/levantamiento_linea_log_views.xml',
        'views/levantamiento_views.xml',
        'views/tipo_elemento_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'levantamiento_medidas/static/src/js/x2many_fullscreen_open_patch.js',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/banner.png'],
}

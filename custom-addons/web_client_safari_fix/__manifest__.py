# -*- coding: utf-8 -*-
{
    'name': 'Web Safari Fix',
    'version': '15.0',
    'category': 'Technical',
    'sequence': 100,
    'summary': 'Fix Safari issue in Odoo 15th version.',
    'description': "Fix Safari issue in Odoo 15th version.",
    'website': '',
    'depends': [
        'base',
    ],
    'data': [
        'views/templates.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'assets': {
        'web.assets_safari_fix': [
            'web_client_safari_fix/static/src/js/event-target@1.2.3.min.js',
            'web_client_safari_fix/static/src/js/ResizeObserver.global.js',
            'web_client_safari_fix/static/src/js/polyfill.min.js',
        ]
    },
    'external_dependencies': {
        'python': [],
        'bin': []
    },
    'license': 'LGPL-3',
}


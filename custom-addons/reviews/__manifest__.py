# -*- coding: utf-8 -*-
{
    'name': 'Reviews',
    'version': '15.0',
    'category': 'Reviews',
    'sequence': 100,
    'summary': 'Reviews module of Odoo 15th version.',
    'description': "Reviews",
    'website': '',
    'depends': [
        'base', 'web', 'hr'
    ],
    'data': [
        'security/reviews_security.xml',
        'security/ir.model.access.csv',

        'data/data.xml',

        'views/templates.xml',

        'report/department_review_qr.xml',

        'views/reviews.xml',
        'views/collection.xml',
        'views/hr_department.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'assets': {
        'reviews.reviews_assets': [
            'reviews/static/src/js/jquery.validate.min.js',
            'reviews/static/src/js/reviews.js',

            'reviews/static/src/scss/reviews.scss',
        ],
        'web.assets_backend': [
            # Styles
            # 'template_empty_module/static/src/scss/demo.scss',
            # Javascript
            # 'template_empty_module/static/src/js/demo.js',
        ],
        'web.report_assets_common': [
            # Styles for the report
        ],
        'web.assets_frontend': [],
        'web.assets_tests': [],
        'web.qunit_suite_tests': [],
        'web.assets_qweb': [
            # 'template_empty_module/static/src/xml/demo.xml',
        ],
    },
    'external_dependencies': {
        'python': [],
        'bin': []
    },
    'license': 'LGPL-3',
}

# -*- coding: utf-8 -*-
{
    'name': "HR Learn Platform",

    'summary': """HR Learn Platform""",

    'description': """
        HR Learn Platform
    """,

    'author': "Pantilei Ianulov",
    'website': "http://www.yourcompany.com",

    'category': 'Technical',
    'version': '15.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizards/employee_assign_course.xml',

        'views/hr_employee.xml',

        'data/data.xml',
        'data/cron.xml',

    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'assets': {
        'web._assets_primary_variables': [],
        'web.assets_backend': [],
        'web.assets_frontend': [],
        'web.assets_tests': [],
        'web.qunit_suite_tests': [],
        'web.report_assets_common': [],
        'web.assets_qweb': [],
    },
    'license': 'LGPL-3',
}

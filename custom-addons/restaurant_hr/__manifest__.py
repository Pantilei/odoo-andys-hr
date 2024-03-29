# -*- coding: utf-8 -*-
{
    'name': "Restaurant HR",

    'summary': """Restaurant HR""",

    'description': """
        Restaurant HR
    """,

    'author': "Pantilei Ianulov",
    'website': "http://www.yourcompany.com",

    'category': 'Technical',
    'version': '15.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base', 'web', 'muk_web_theme', 'hr', 'hr_skills', 
        'hr_organizational_chart', 'survey', 'hr_recruitment'
    ],

    # always loaded
    'data': [
        'security/restaurant_hr_security.xml',
        'security/ir.model.access.csv',

        'views/hr_employee.xml',
        'views/hr_department.xml',
        'views/survey_survey.xml',
        'views/survey_user_input.xml',
        'views/hr_applicant.xml',
        'views/hr_job.xml',
        'views/hr_job_group.xml',
        'views/hr_branch.xml',
        'views/hr_qualification.xml',
        'views/staff_of_workers_report.xml',

        'views/department_history.xml',
        'views/hr_dep_org_chart.xml',

        'wizards/employee_survey_select_wizard.xml',
        'wizards/applicant_survey_select_wizard.xml',
        'wizards/department_history_report.xml',
        'wizards/employee_assign_survey.xml',

        'reports/hr_employee_badge.xml',
        'reports/employee_card_report.xml',

        'templates/employee_card_template.xml',

        'views/menu_items.xml',

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
        'web.assets_backend': [

            'restaurant_hr/static/libs/d3_orgchart/d3.v7.min.js',
            'restaurant_hr/static/libs/d3_orgchart/d3-org-chart.js',
            'restaurant_hr/static/libs/d3_orgchart/d3-flextree.js',


            'web/static/lib/Chart/Chart.js',

            'restaurant_hr/static/src/js/action_menus.js',
            'restaurant_hr/static/src/js/json_to_chart_widget.js',
            'restaurant_hr/static/src/js/department_org_chart.js',
            'restaurant_hr/static/src/scss/department_org_chart.scss',

            'restaurant_hr/static/src/js/employee_card_widget.js',
        ],
        'web.assets_frontend': [],
        'web.assets_tests': [],
        'web.qunit_suite_tests': [],
        'web.report_assets_common': [],
        'web.assets_qweb': [
            'restaurant_hr/static/src/xml/json_to_chart_widget.xml',
            'restaurant_hr/static/src/xml/department_org_chart.xml',
            'restaurant_hr/static/src/xml/employee_card_widget.xml',
        ],
    },
    'license': 'LGPL-3',
}

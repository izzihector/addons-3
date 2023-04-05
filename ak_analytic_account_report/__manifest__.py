# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Analytic Account Report',
    'version': '14.0.1.0.0',
    'category': 'Purchases',
    'summary': 'Analytic Account Report',
    'description': "Analytic Account Report",
    'author': "Boraq-Group",
    'website': 'https://boraq-group.com',
    'depends': ['account', 'sr_property_rental_management'],
    "license": "AGPL-3",
    'data': [
        'security/ir.model.access.csv',
        'report/analytic_account_report_template.xml',
        'report/report.xml',
        'wizard/analytic_account_report_wizard_view.xml',
    ],
    "images": ['static/description/banner.png'],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}

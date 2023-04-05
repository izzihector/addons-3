# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'AK Service Fees Report',
    'version': '14.0.1.0.0',
    'category': 'Accounting',
    'summary': 'AK Service Fees Report',
    'description': "AK Service Fees Report",
    'author': "Pure IT Solution",
    'website': 'https://boraq-group.com',
    'depends': ['account', 'accounting_pdf_reports'],
    "license": "AGPL-3",
    'data': [
        'security/ir.model.access.csv',
        'report/ak_service_fees_template.xml',
        'report/report.xml',
        'wizard/ak_service_wizard_view.xml',
    ],
    "images": ['static/description/banner.png'],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}

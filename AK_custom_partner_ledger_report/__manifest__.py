# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Company Partner Ledger Report',
    'version': '14.0.1.0.0',
    'category': 'Purchases',
    'summary': 'Company Partner Ledger Report',
    'description': "Company Partner Ledger Report",
    'author': "Boraq-Group",
    'website': 'https://boraq-group.com',
    'depends': ['account', 'accounting_pdf_reports'],
    "license": "AGPL-3",
    'data': [
        'security/ir.model.access.csv',
        'view/inherited_account_payment_view.xml',
        'report/custom_partner_ledger_template.xml',
        'report/report.xml',
        'wizard/partner_ledger_wizard_view.xml',
    ],
    "images": ['static/description/banner.png'],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}

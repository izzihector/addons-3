# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

{
    "name": "Cancel Invoice | Cancel Payment",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Accounting",
    "license": "OPL-1",
    "summary": "Cancel Account, Cancel Invoices, Cancel Payments,Invoice Cancel, Payment Cancel, Cancel Bill,,Bill Cancel, Cancel Receipts, Accounting Cancel,Delete Account,Delete Invoices,Delete Payments, Delete Bills, Remove Invoice,Remove Bill Odoo",
    "description": """This module helps to cancel invoice & payment. You can also cancel multiple invoices & payments from the tree view. You can cancel the invoice & payment in 3 ways,

1) Cancel Only: When you cancel an invoice & payment then the invoice & payment are cancelled and the state is changed to "cancelled".
2) Cancel and Reset to Draft: When you cancel the invoice & payment, first invoice & payment are cancelled and then reset to the draft state.
3) Cancel and Delete: When you cancel the invoice & payment then first the invoice & payment are cancelled and then the invoice & payment will be deleted.""",
    "version": "14.0.1",
    "depends": [
                "account",

    ],
    "application": True,
    "data": [
        'security/account_security.xml',
        'data/data.xml',
        'views/res_config_settings.xml',
        'views/views.xml',
    ],
    "images": ["static/description/background.png", ],
    "auto_install": False,
    "installable": True,
    "price": 20,
    "currency": "EUR"
}

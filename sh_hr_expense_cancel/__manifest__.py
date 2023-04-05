# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

{
    "name": "Cancel HR Expense",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Human Resources",
    "license": "OPL-1",
    "summary": "HR Expense Cancel,Delete HR Expense, Cancel Expenses, Cancel Expense report, Cancel And Reset HR Expense, refuse HR Expense, HR Expense Refuse, Expense Refuse, Cancel Multiple Expenses, Mass Expenses Cancel,Delete Expenses Odoo",
    "description": """This module helps to cancel/refuse expenses. You can also cancel multiple expenses from the tree view. You can cancel the expenses in 3 ways,

1) Cancel Only: When you cancel the expense then the expenses are canceled and the state is changed to "Refused".
2) Cancel and Reset to Draft: When you cancel the expenses, first expenses are canceled and then reset to the draft state.
3) Cancel and Delete: When you cancel the expenses then first the expenses are canceled and then the expenses will be deleted. """,
    "version": "14.0.1",
    "depends": [
                "hr_expense",

    ],
    "application": True,
    "data": [
        'security/hr_security.xml',
        'data/data.xml',
        'views/hr_config_settings.xml',
        'views/views.xml',
    ],
    "images": ["static/description/background.png", ],
    "auto_install": False,
    "installable": True,
    "price": 20,
    "currency": "EUR"
}

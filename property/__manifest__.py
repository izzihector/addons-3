# -*- coding: utf-8 -*-
{
    'name': "Property",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Property
    """,

    'author': "By pure It solution custom property module",
    'website': "http://www.yourcompany.com",


    'category': 'Sales & Rent',
    'version': '1.0',
    "images":['static/logo.png'],
    'depends': ['base','property_rental_mgt_app'],
    'data': [
            'security/ir.model.access.csv',
            'views/product.xml',
            'views/property_reserve.xml',
            'views/hisory_renter.xml',
            'views/contract_details.xml',
            # 'views/account_move_line.xml',
            'views/account.accont.xml',
            #'views/templates_veiws.xml',
            # 'views/contract_template_views.xml',
            'report/renter_card_report_teamplate_pdf.xml',
            'report/contract_report_templates.xml',
            'report/report_hr_contract_appendix.xml',
            'report/report_rent_contract.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}

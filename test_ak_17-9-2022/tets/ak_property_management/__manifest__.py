{
    'name': 'AK Property Home',
    'version': '14.0',
    'summary': 'Summery',
    'description': 'Description',
    'category': 'Category',
    'author': 'Author',
    'depends': ['sr_property_rental_management','maintenance', 'base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/all_xml_in_one.xml',
        'views/maintanance.xml',
        'views/generators.xml',
        'wizard/property_maintenance_wizard_view.xml',
        'reports/renter_card_report_teamplate_pdf.xml',
        'reports/facility_service_report.xml',
        'reports/contract.xml',
        'reports/deplomatic_contract.xml',
        'reports/property_maintenance_report_template.xml',
        'reports/ak_invoice.xml',
        'reports/report.xml',
    ],

    'installable': True,
    'auto_install': False
}

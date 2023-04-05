# -*- coding: utf-8 -*-
{
    'name': "Imprest Analysis(Custody Analysis)",
    'summary': """This Module to manage Imprest Analysis or Custody Analysis""",
    'description': """This Module to manage Imprest Analysis or Custody Analysis""",

    'author': "ModSaeed",
    'website': "",
    'category': 'accounting',
    'version': '14.0.1',
    'license': 'OPL-1',
    'currency': 'EUR',
    'price': 29.0,
    # any module necessary for this one to work correctly
    'depends': ['base','hr','account','analytic'],
    # always loaded
    'data': [
        'security/imprest_security.xml',
        'security/ir.model.access.csv',
        'data/imprest_sequence_data.xml',
        'views/views.xml',
    ],
    'images': ['static/description/images/images.jpg','static/description/images/images.jpg'],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

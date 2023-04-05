# -*- coding: utf-8 -*-
# from odoo import http


# class ImprestAnalysis(http.Controller):
#     @http.route('/imprest_analysis/imprest_analysis/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/imprest_analysis/imprest_analysis/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('imprest_analysis.listing', {
#             'root': '/imprest_analysis/imprest_analysis',
#             'objects': http.request.env['imprest_analysis.imprest_analysis'].search([]),
#         })

#     @http.route('/imprest_analysis/imprest_analysis/objects/<model("imprest_analysis.imprest_analysis"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('imprest_analysis.object', {
#             'object': obj
#         })

# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AkAccountAnalyticLineInherited(models.Model):
    _inherit = 'account.analytic.line'

    account_id_name = fields.Char(related='account_id.name', store=True)



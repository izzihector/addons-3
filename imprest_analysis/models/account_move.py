# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class Move(models.Model):
    _inherit = "account.move"

    imprest_id = fields.Many2one('imprest.analysis')
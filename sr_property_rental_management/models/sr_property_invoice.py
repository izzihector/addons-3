# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import models, fields, _

class srAccountMove(models.Model):
    _inherit = 'account.move.line'
    
    tenancy_agreement = fields.Many2one('sr.tenancy.agreement', 'Agreement')
    gym_fees  = fields.Float(string = "GYM")
    diesel_fees = fields.Float(string = "Diesel")


    def _prepare_analytic_line(self):
        """ Prepare the values used to create() an account.analytic.line upon validation of an account.move.line having
            an analytic account. This method is intended to be extended in other modules.
            :return list of values to create analytic.line
            :rtype list
        """
        result = []
        for move_line in self:
            amount = (move_line.credit or 0.0) - (move_line.debit or 0.0)
            default_name = move_line.name or (move_line.ref or '/' + ' -- ' + (move_line.partner_id and move_line.partner_id.name or '/'))
            result.append({
                'name': default_name,
                'date': move_line.date,
                'account_id': move_line.analytic_account_id.id,
                'group_id': move_line.analytic_account_id.group_id.id,
                'tag_ids': [(6, 0, move_line._get_analytic_tag_ids())],
                'unit_amount': move_line.quantity,
                'product_id': move_line.product_id and move_line.product_id.id or False,
                'product_uom_id': move_line.product_uom_id and move_line.product_uom_id.id or False,
                'amount': amount,
                'general_account_id': move_line.account_id.id,
                'ref': move_line.ref,
                'move_id': move_line.id,
                'user_id': move_line.move_id.invoice_user_id.id or self._uid,
                'partner_id': move_line.partner_id.id,
                'company_id': move_line.analytic_account_id.company_id.id or move_line.move_id.company_id.id,
                'owner_id': move_line.move_id.owner_id.id,
            })
        return result


class srAccountMove(models.Model):
    _inherit = 'account.move'

    is_property_invoice = fields.Boolean('Is Property Invoice?')
    property_id = fields.Many2one('product.product', 'Property')
    tenancy_agreement = fields.Many2one('sr.tenancy.agreement', string="Tenancy Agreement")
    is_property_commission_bill = fields.Boolean('Is Property Commission Invoice?')
    owner_id = fields.Many2one('res.partner', string="Owner")
    duration = fields.Char(string = "Duration")
    payment_term = fields.Char(string = "Payment Terms")
    ak_invoice_type = fields.Selection([
                                        ('general_invoice', 'General Invoice'),
                                        ('five_fees_invoice', '5% Invoice'),
                                        ('club_fees_invoice', 'Club Fees Invoice'),
                                        ])
    

      # tenant_id = fields.Many2one('res.partner', string="Tenent")

class AkAnalyticAccountInherit(models.Model):
    _inherit = 'account.analytic.line'

    owner_id = fields.Many2one('res.partner', string = "Owner")



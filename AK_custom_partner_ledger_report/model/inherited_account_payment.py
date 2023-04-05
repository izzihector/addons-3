from odoo import fields, models, api, _

class AccountPaymentRegisterInherited(models.TransientModel):
    _inherit = 'account.payment.register'

    owner = fields.Many2one('res.partner', string = "Owner")
    property_id = fields.Many2one('product.product', string = "Property")

    @api.model
    def _get_line_batch_key(self, line):
        ''' Turn the line passed as parameter to a dictionary defining on which way the lines
        will be grouped together.
        :return: A python dictionary.
        '''
        return {
            'partner_id': line.partner_id.id,
            'account_id': line.account_id.id,
            'currency_id': (line.currency_id or line.company_currency_id).id,
            'partner_bank_id': (line.move_id.partner_bank_id or line.partner_id.commercial_partner_id.bank_ids[:1]).id,
            'partner_type': 'customer' if line.account_internal_type == 'receivable' else 'supplier',
            'payment_type': 'inbound' if line.balance > 0.0 else 'outbound',
            'owner': line.owner.id,
            'property_id': line.property_id.id,
        }






class AccountMoveInherited(models.Model):
    _inherit = 'account.move'

    def action_register_payment(self):
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        '''
        return {
        'name': _('Register Payment'),
        'res_model': 'account.payment.register',
        'view_mode': 'form',
        'context': {
            'active_model': 'account.move',
            'active_ids': self.ids,
            # 'default_owner': self.partner_id.id,
            'default_owner': self.owner_id.id,
            'default_property_id': self.property_id.id
            
        },
        'target': 'new',
        'type': 'ir.actions.act_window',
        }


class AccountPaymentInherited(models.Model):
    _inherit = 'account.payment'

    owner = fields.Many2one('res.partner', string = "Owner")
    property_id = fields.Many2one('product.product', string = "Property")

    def _create_payment_vals_from_wizard(self):
        payment_vals = {
            'date': self.payment_date,
            'amount': self.amount,
            'payment_type': self.payment_type,
            'partner_type': self.partner_type,
            'ref': self.communication,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_bank_id': self.partner_bank_id.id,
            'payment_method_id': self.payment_method_id.id,
            'destination_account_id': self.line_ids[0].account_id.id,
            'owner': self.owner.id,
            'property_id': self.property_id.id
        }

        if not self.currency_id.is_zero(self.payment_difference) and self.payment_difference_handling == 'reconcile':
            payment_vals['write_off_line_vals'] = {
                'name': self.writeoff_label,
                'amount': self.payment_difference,
                'account_id': self.writeoff_account_id.id,
            }
        return payment_vals


class AccountMoveLineInherited(models.Model):
    _inherit = 'account.move.line'

    owner = fields.Many2one('res.partner', string = "Owner")
    property_id = fields.Many2one('product.product', string = "Property")
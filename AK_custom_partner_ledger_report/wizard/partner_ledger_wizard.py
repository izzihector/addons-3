from odoo import models, fields, api

class AkPartnerLedgerReport(models.TransientModel):
    _name = 'ak.partner.ledger.wizard'


    property_id = fields.Many2one('product.product', string = "Property", required = True)
    start_date = fields.Date(string = "Start Date")
    end_date = fields.Date(string = "End Date")

    def print_report(self):

        partner_ledger = self.env['account.move.line'].search([('move_id.property_id.id', '=', self.property_id.id),('journal_id.type', 'not in', ['cash', 'bank']),('account_id', 'in', [self.property_id.property_account_income_id.id,self.property_id.property_account_expense_id.id]),('date', '>=', self.start_date), ('date', '<=', self.end_date)])
        print('################################', partner_ledger)
        data = {
                'property_id': self.property_id.name,
                'owner': self.property_id.property_landlord_id.name,
                'start_date': self.start_date,
                'end_date': self.end_date,
        }
        record = []
        balance = 0
        total_debit = 0
        total_credit = 0
        for rec in partner_ledger:
            balance =  rec.credit - rec.debit + balance
            re = {
                    'date': rec.date,
                    'journal_id': rec.journal_id.name,
                    'move_id': rec.move_id.name,
                    'account_id': rec.account_id.code + ' ' + rec.account_id.name,
                    'partner_id': rec.partner_id.name,
                    'name': rec.name,
                    'ref': rec.ref,
                    'debit': rec.debit,
                    'credit': rec.credit,
                    'balance': balance 
            }
            total_debit += re['debit']
            total_credit += re['credit']
            record.append(re)
        dcb = {
                'total_debit': total_debit,
                'total_credit': total_credit,
                'balance': balance
        }
        res = {
                'record': record,
                'data': data,
                'dcb': dcb
        }
                
        return self.env.ref('AK_custom_partner_ledger_report.ak_custom_partner_ledger_report').report_action(self, data=res)
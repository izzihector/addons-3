from odoo import fields,api, models, _


class LedgerWizard(models.TransientModel):
    # _inherit = 'account.common.partner.report'
    _name = 'general.ledger.wizard'

    partner_id = fields.Many2one('res.partner',required=True,store=True)

    def print_report(self):
        data = {
            'partner_id': self.partner_id.name
        }
        res = { }
        cr = self.env.cr
        query = """
                select m.ref,m.name as doc_no, m.date, m.narration, j.name as journal, p.name as partner_name,
                l.name as line_desc, a.name as gl_account, m.currency_id, l.debit, l.credit
                from account_move_line l
                join account_move m on l.move_id = m.id
                join res_partner p on l.partner_id = p.id
                join account_account a on l.account_id = a.id
                join account_journal j on m.journal_id = j.id
                where l.partner_id = %s
                and a.reconcile = True
                order by m.date """%(self.partner_id.name) #and a.reconcile = True

        cr.execute(query)
        record = cr.dictfetchall()
        # Start for sum debit and cridet
        cr = self.env.cr
        query = """select sum(l.debit - l.credit) as opening_bal
                from account_move_line l
                join account_move m on l.move_id = m.id
                join account_account a on l.account_id = a.id
                where a.reconcile = True
                and l.partner_id = %s""" % (self.partner_id.id)

        cr.execute(query)
        openbal = cr.dictfetchall()
        # End Query
        res = {
                'record':record,
                'data':data,
                'openbal':openbal
        }
        print ("=====================>", res)
        return self.env.ref('property_rental_mgt_app.general_ledger_report_as_pdf').report_action(self, data=res)


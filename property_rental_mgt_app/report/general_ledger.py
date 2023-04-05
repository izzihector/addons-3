import time
from datetime import datetime
import collections
from odoo import api, fields, models


class PartnerLedger(models.AbstractModel):
    _name = 'report.property_rental_mgt_app.general_ledger_template'
 
    @api.model
    def _get_report_values(self,docids,data):
        # data['computed'] = {}
        params = data['form'].get('partner_id')
        cr = self.env.cr
        query = ("""
        select m.ref,m.name as doc_no, m.date, m.narration, j.name as journal, p.name as partner_name, 
        l.name as line_desc, a.name as gl_account, m.currency_id, l.debit, l.credit
        from account_move_line l
        join account_move m on l.move_id = m.id
        join res_partner p on l.partner_id = p.id
        join account_account a on l.account_id = a.id
        join account_journal j on m.journal_id = j.id
        where a.reconcile = True
        and l.partner_id = %s
        order by m.date """,tuple(params))


        cr.execute(query)
        record = cr.dictfetchall()
        result = {'docs': record,
                'data': data,
                }
        print("The Result Is", result)

#and l.partner_id = %s         where a.reconcile = True

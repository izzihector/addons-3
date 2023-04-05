from itertools import groupby
# from attr import field
from odoo import models, fields, api

class AnalyticAccountReport(models.TransientModel):
    _name = 'analytic.account.report.wizard'

    analytic_account_ids = fields.Many2many('account.analytic.account', string = "Analytic Account")
    start_date = fields.Date(string = "Start Date")
    end_date = fields.Date(string = "End Date")

    def print_report(self):
        
        ac_list = []
        for ac in self.analytic_account_ids:
                ac_list.append(ac.name)
        
        print("------------>", ac_list)
                
        analytic_account_group = self.env['account.analytic.line'].read_group([('account_id.name', 'in', ac_list), ('date', '>=', self.start_date), ('date', '<=', self.end_date)], fields = ['account_id_name'], groupby = ['account_id_name'], lazy = False)
        analytic_account_rec = self.env['account.analytic.line'].search([('account_id.name', 'in', ac_list), ('date', '>=', self.start_date), ('date', '<=', self.end_date)])
        data = {
                'start_date': self.start_date,
                'end_date': self.end_date,
        }
        record = []
        for rec in analytic_account_rec:
            re = {
                    'general_account_id': rec.general_account_id.name,
                    'name': rec.account_id.name,
                    'description': rec.name,
                    'date': rec.date,
                    'owner_id': rec.owner_id.name,
                    'amount': rec.amount, 
            }
            record.append(re)

        print("------------>", analytic_account_group)
        # print("------------>", analytic_account_group[0]['account_id_name'])
        print("------------>", analytic_account_rec)
        
        res = {
                'record': record,
                'data': data,
                'analytic_account_group': analytic_account_group,

        }
                
        return self.env.ref('ak_analytic_account_report.custom_analytic_account_report').report_action(self, data=res)
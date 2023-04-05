from odoo import models, fields, api

class AkServiceFees(models.TransientModel):
    _name = 'ak.service.fees.wizard'


    start_date = fields.Date(string = "Start Date")
    end_date = fields.Date(string = "End Date")

    def print_report(self):

        service_fees = self.env['account.move.line'].search([('account_id.code', 'in', ['600001', '600002', '600003', '600004', '600005', '600006', '600007', '600008', '400300']), ('date', '>=', self.start_date), ('date', '<=', self.end_date)])
        data = {
                'start_date': self.start_date,
                'end_date': self.end_date,
        }
        total_adminstrative_cost = 0
        total_power_supply_generator = 0
        total_acs_maintenance = 0
        total_plumbing_works = 0
        total_security = 0
        total_gardening = 0
        total_cleaning = 0
        total_replacement_renewal = 0
        total_service_cost = 0

        for rec in service_fees:
                if rec.account_id.code == '600001':
                        total_adminstrative_cost += rec.debit
                
                if rec.account_id.code == '600002':
                        total_power_supply_generator += rec.debit

                if rec.account_id.code == '600003':
                        total_acs_maintenance += rec.debit
                
                if rec.account_id.code == '600004':
                        total_plumbing_works += rec.debit
                
                if rec.account_id.code == '600005':
                        total_security += rec.debit

                if rec.account_id.code == '600006':
                        total_gardening += rec.debit

                if rec.account_id.code == '600007':
                        total_cleaning += rec.debit

                if rec.account_id.code == '600008':
                        total_replacement_renewal += rec.debit

                if rec.account_id.code == '200100':
                        total_service_cost += rec.debit
          
        sf = {
                'total_adminstrative_cost': total_adminstrative_cost,
                'total_power_supply_generator': total_power_supply_generator,
                'total_acs_maintenance': total_acs_maintenance,
                'total_plumbing_works': total_plumbing_works,
                'total_security': total_security,
                'total_gardening': total_gardening,
                'total_cleaning': total_cleaning,
                'total_replacement_renewal': total_replacement_renewal,
                'total_service_cost': total_service_cost, 
                'total_of_total': total_adminstrative_cost + total_power_supply_generator + total_acs_maintenance + total_plumbing_works + total_security + total_gardening + total_cleaning + total_replacement_renewal, 
        }
        res = {
                'data': data,
                'sf': sf
        }
                
        return self.env.ref('AK_service_fees_report.ak_service_fees_report').report_action(self, data=res)
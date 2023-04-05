from odoo import models, fields, api

class AkPropertyMaintenanceReport(models.TransientModel):
    _name = 'ak.property.maintenance.report'


    property_id = fields.Many2one('product.product', string = "Property", required = True)
    start_date = fields.Date(string = "Start Date")
    end_date = fields.Date(string = "End Date")

    def print_report(self):

        property_maintenance = self.env['property.maintanance'].search([('property_id.name', '=', self.property_id.name), ('date_from', '>=', self.start_date), ('date_to', '<=', self.end_date)])
        data = {
                'property_id': self.property_id.name,
                'owner': self.property_id.property_landlord_id.name,
                'start_date': self.start_date,
                'end_date': self.end_date,
        }
        record = []
        for rec in property_maintenance:
            re = {
                    'name': rec.name,
                    'property_id': rec.property_id.name,
                    'date_from': rec.date_from,
                    'date_to': rec.date_to,
                    'generator_id': rec.generator_id.name,
                    'maintain_cost': rec.maintain_cost,
                    'operation': rec.operation,
                    'state': rec.state,
                    'description': rec.description, 
            }
            record.append(re)
      
        res = {
                'record': record,
                'data': data,
        }
                
        return self.env.ref('ak_property_management.property_maintenance_report').report_action(self, data=res)
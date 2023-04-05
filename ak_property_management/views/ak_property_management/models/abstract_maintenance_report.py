from odoo import fields, models, api
# from odoo.tools.amount_to_text_en import amount_to_text


class MaintenanceReportAbstract(models.AbstractModel):
	_name = 'report.ak_property_management.property_maintenance_template'


	@api.model
	def _get_report_values(self, docids, data=None):

            result = self.env['property.maintanance'].search([])
            print("------------>", result)


            return {
            'docs' : result,
            }
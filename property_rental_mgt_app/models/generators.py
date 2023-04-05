from odoo import api, fields, models
from datetime import datetime
import time

class GeneratorsMonitoring(models.Model):
    _name = 'generators.monitoring'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Generator", required=True)
    serial_number = fields.Char(string="Serial")
    manufacturing_date = fields.Date('Manufacturing Date')
    tank_capacity = fields.Float(string="Capacity Of Tank")
    generator_ids = fields.One2many('generator.line','generator_id')
    amount_total = fields.Float(string="Total", readonly=True)
    invoice_count = fields.Integer("#Invoice", compute='_compute_invoice_count')
    maintain_count =  fields.Integer("#Maintain", compute='_compute_maintanance')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id)

    @api.depends()
    def _compute_maintanance(self):
	    for rec in self:
		    maintanance = self.env['property.maintanance'].search([('generator_id','=',rec.id)])
		    rec.maintain_count = len(maintanance)

    @api.onchange('generator_ids')
    def _calc_amount_total(self):
        result = sum(generator_id.cost for generator_id in self.generator_ids)
        self.amount_total = result
        # print("============>",self.all_consuming)
    


    def action_view_maintenance(self):
	    for rec in self:
		    maint = self.env['property.maintanance'].search([('generator_id','=',rec.id)])
		    action = self.env.ref('property_rental_mgt_app.action_maintanance').read()[0]
		    if len(maint) > 1:
		    	action['domain'] = [('id', 'in', maint.ids)]
		    elif len(maint) == 1:
		    	action['views'] = [(self.env.ref('property_rental_mgt_app.property_maintanance_form').id, 'form')]
		    	action['res_id'] = maint.ids[0]
		    else:
		    	action = {'type': 'ir.actions.act_window_close'}
		    return action


class GeneratorLine(models.Model):
    _name = 'generator.line'

    start_date = fields.Datetime(string="Starting Date")
    capacity_when_start = fields.Float(string="Capacity When Start")
    pause_date = fields.Datetime(string="Pausing Date")
    capacity_when_stop = fields.Float(string="Capacity When Stop")
    consuming = fields.Float(string="Consuming Foul", readonly=True)
    total_time = fields.Datetime(string="Time")
    generator_id = fields.Many2one('generators.monitoring')
    cost = fields.Float(string="Cost", readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id)

    @api.onchange('capacity_when_start','capacity_when_stop')
    def _calc_consuming_foul(self):
        self.consuming = self.capacity_when_start - self.capacity_when_stop


    @api.onchange('consuming')
    def clac_cost_of_consuming(self):
        price_obj = self.env['diesel.pricing'].search([])
        for rec in self:
            c = rec.consuming * price_obj.price
            rec.cost = c

    # @api.onchange('start_date','pause_date')
    # def _calc_consuming_times(self):
    #     for rec in self:
    #         rec.start_date = time.strftime('%Y-%m-%d %H:%M:%S')
    #         rec.pause_date = time.strftime('%Y-%m-%d %H:%M:%S')
    #         rec.total_time = rec.pause_date - rec.start_date
    #         print("====================>",rec.total_time)
  # @api.onchange('start_date','pause_date')
  #   def _calc_consuming_times(self):
  #       for rec in self:
  #           rec.start_date = time.strftime('%Y-%m-%d %H:%M:%S')
  #           rec.pause_date = time.strftime('%Y-%m-%d %H:%M:%S')
  #           rec.total_time = rec.pause_date - rec.start_date
  #           print("====================>",rec.total_time)
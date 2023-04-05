from odoo import fields, models, api
import datetime
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

# class AccountInh(models.Model):
#     _inherit = 'account.move'

#     owner_id = fields.Many2one('res.partner', string="Owner")


class Product(models.Model):
    _inherit = 'product.product'

    property_size = fields.Float(string="Property Size Area")
    property_maintenance_charge = fields.Float(compute="clac_maintenance_charge")
    property_no = fields.Char(string="Property NO")
    wifi = fields.Char(string="Wifi")
    wifi_username = fields.Char(string="Wifi username")
    wifi_password = fields.Char(string="Wifi password")
    meter = fields.Float(string="Electricity Meter Number")
    meter_kw_in_arriving = fields.Float(string="Meter KW Arriving")
    meter_kw_in_departure = fields.Float(string="Meter KW Departure")
    club_fees = fields.Float(string="Gym")
    diesel_fees = fields.Float(string="Diesel")
    # facility_ids = fields.One2many('facility.services.line', 'property_id')

    @api.depends('property_maintenance_charge')
    def clac_maintenance_charge(self):
        ps = self.env['property.size'].search([])

        self.property_maintenance_charge = self.property_size * ps.price

    def create_maintenance_invoice(self):
        invoice_vals = {
            'partner_id': self.property_landlord_id.id,
            'state': 'draft',
            'invoice_date': datetime.datetime.today().date(),
            'is_property_invoice': True,
            'property_id': self.id,
            'invoice_payment_term_id': 1,
            'move_type': 'in_invoice',
            'invoice_line_ids': [(0, 0, {
                'product_id': self.id,
                'name': self.name +''+"Service Cost",
                'quantity': 1,
                'price_unit': self.property_maintenance_charge,
            })]
        }
        # self.state = 'invoiced'
        invoice = self.env['account.move'].sudo().create(invoice_vals)
        return invoice

class ContractCon(models.Model):
    _inherit ='sr.tenancy.agreement'

    facility_ids = fields.One2many('facility.lines', 'rel_id')
    deposit = fields.Float(string="Deposit")
    terms_conditionas = fields.Text(string="Terms of payment")
    gym = fields.Selection([('inc','Include'),('not_inc','Not include')])
    diesel = fields.Selection([('inc','Include'),('not_inc','Not include')])
    gym_fee = fields.Float(related="property_id.club_fees")
    diesel_fee = fields.Float(related="property_id.diesel_fees")
    time = fields.Char(compute="make_time")

    @api.depends('time')
    def make_time(self):
        for rec in self:
            rec.time = str(rec.agreement_duration) +''+ str(rec.agreement_duration_type)



 

    @api.depends('property_id', 'agreement_start_date', 'agreement_duration', 'agreement_duration_type','gym', 'diesel')
    def _compute_amount_all(self):
        for order in self:
            num_months = 0
            if order.agreement_start_date and order.agreement_duration and order.agreement_duration_type:
                if order.agreement_duration_type == 'month':
                    order.agreement_expiry_date = order.agreement_start_date + relativedelta(months=order.agreement_duration)
                else:
                    order.agreement_expiry_date = order.agreement_start_date + relativedelta(years=order.agreement_duration)
                num_months = (order.agreement_expiry_date.year - order.agreement_start_date.year) * 12 + (order.agreement_expiry_date.month - order.agreement_start_date.month)
                difference = relativedelta(order.agreement_expiry_date, order.agreement_start_date)
            else:
                order.agreement_expiry_date = False
                
            if order.property_id.property_type == 'rent':
                commission = 0
                if order.commission_type == 'percentage':
                    commission = (num_months * order.property_id.property_rent_price) * (order.agent_commission / 100)
                else:
                    commission = order.agent_commission
                plus_gym = 0
                if order.agreement_duration_type == 'month': 
                    if order.gym == 'inc':
                        plus_gym = (order.gym_fee * order.agreement_duration)
                    else : plus_gym = 0

                if order.agreement_duration_type == 'year': 
                    if order.gym == 'inc':
                        plus_gym = (order.gym_fee * order.agreement_duration) * 12
                    else : plus_gym = 0

                diesel_plus = 0
                if order.agreement_duration_type == 'month': 
                    if order.diesel == 'inc':
                        diesel_plus = (order.diesel_fee * order.agreement_duration)
                    else : diesel_plus = 0

                if order.agreement_duration_type == 'year': 
                    if order.diesel == 'inc':
                        diesel_plus = (order.diesel_fee * order.agreement_duration) * 12
                    else : diesel_plus = 0

                order.update({
                    'total_price': num_months * order.property_id.property_rent_price,
                    # 'commission_price':commission,
                    'final_price' : (num_months * order.property_id.property_rent_price) + commission + plus_gym + diesel_plus
                })
            elif order.property_id.property_type == 'sale':
                if order.commission_type == 'percentage':
                    commission = (order.property_sale_price) * (order.agent_commission / 100)
                else:
                    commission = order.agent_commission
                order.update({
                    'total_price': order.property_sale_price,
                    # 'total_maintenance':order.maintenance_charge,
                    # 'commission_price':commission,
                    'final_price' : commission + order.property_sale_price
                })
            else:
                order.update({
                    'total_price': 0,
                    # 'total_maintenance':0,
                    # 'commission_price':0,
                    'final_price' : 0
                })

    @api.model
    def default_get(self, fields):
        result = super(ContractCon, self).default_get(fields)
        facility_ids = [(5, 0, 0)]
        f_obj = self.env['property.facility'].search([])
        for f in f_obj:
            line = (0 ,0,{
                'facility_id' : f.id,
            })
            facility_ids.append(line)
        result.update({
            'facility_ids' : facility_ids
        })
        return result
    
class FacilityServicesLine(models.Model):
	_name = 'facility.lines'

	facility_id = fields.Many2one('property.facility', required=True, store=True, string="Checklist")
	count = fields.Integer(string="Count", required=True)
	disc = fields.Char(related="facility_id.disc" ,string="Description")
	is_exist = fields.Boolean(string="Existing ?", required=True)
	rel_id = fields.Many2one('sr.tenancy.agreement')
	categ_id = fields.Many2one('facility.category', string = "Category")
	brand = fields.Binary(string = "Brand")
    # related="facility_id.categ_id"
    # related="facility_id.brand"




	@api.onchange('is_exist')
	def set_count_to_zero_for_facility_when_not_exist(self):
		for rec in self:
			if not rec.is_exist:
				rec.count = 0



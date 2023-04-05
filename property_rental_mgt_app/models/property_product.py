# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date
from dateutil import relativedelta
from odoo.exceptions import ValidationError
#from pyasn1_modules.rfc6031 import at_pskc_issuer
# from stdnum.exceptions import ValidationError


class ProductProduct(models.Model):
	_inherit = 'product.product'

	invoice_count = fields.Integer("#Invoice", compute='_compute_invoice_count')
	contract_count = fields.Integer("#Contract", compute='_compute_contract_count')
	maintain_count =  fields.Integer("#Maintain", compute='_compute_maintanance')
	is_property = fields.Boolean(string="Property")
	deposite = fields.Float("Total Rent Cost")
	maintain_charge = fields.Float(compute="calc_price_of_size",string="Maintenance Charge")
	reasonable_price = fields.Boolean("Allow Discount(%)")
	owner_id = fields.Many2one('res.partner', string="Property Owner", domain=[('partner_type','=','owner')])
	user_id = fields.Many2one('res.users', string="Login User")
	salesperson_id = fields.Many2one('res.users', string="Salesperson",default=lambda self: self.env.user)
	property_book_for = fields.Selection([('sale','Sale'),('rent','Rent')],default="rent", string=" Property Type", help="property reserve for rent and sale.")
	property_type = fields.Many2one('property.type')
	area = fields.Float("Size area")
	rent_price = fields.Float("Property Rent")
	reasonable_rent = fields.Boolean("Allow Discount in(%)")
	discounted_price = fields.Float("Reasonable Price")
	property_price = fields.Float()
	partial_payment_ids = fields.Many2many('partial.payment','property_partial_payment', string='Allow Partial Payment' )
	user_commission_ids = fields.One2many('user.commission', 'property_id', string="Commission" )
	renter_history_ids = fields.One2many('renter.history', 'property_id' ) 
	state = fields.Selection([('draft','Draft'),('rent','Available'),('under_maintenance','Under Maintenance'),('reserve','Reserve'),('occ','Occupied'),('sale','Saleable'),('cancel','Cancelled')], string="Property Status", track_visibility="onchange", help='State of the Propertsy')
	property_floor = fields.Integer()
	construction_status = fields.Char("Construction Status",default="Ready to Move")
	plot_area = fields.Char()
	invoice_ids = fields.Many2many('account.move', 'partial_payment_account_invoice')
	wifi = fields.Char(string="Wifi")
	wifi_username = fields.Char(string="Wifi username")
	wifi_password = fields.Char(string="Wifi password")
	bedrooms  = fields.Char()
	balconies = fields.Integer()
	washroom = fields.Integer()
	hall = fields.Integer()
	villa_number = fields.Integer()
	meter = fields.Integer(string="Electricity Meter Number")
	meter_kw_in_arriving = fields.Float(string="Meter KW Arriving")
	meter_kw_in_departure = fields.Float(string="Meter KW Departure")
	club_fees = fields.Float(string="Gym")
	diesel_fees = fields.Float(string="Diesel")
	more_details = fields.Text("More Details")
	rent_unit = fields.Selection([('monthly','Monthly'),('yearly','Yearly')], default='monthly')
	property_avl_from = fields.Date("Property Exist From")
	is_partial = fields.Boolean()
	is_reserved = fields.Boolean()
	is_sold = fields.Boolean()
	age = fields.Integer('Property Age')
	months = fields.Integer('Months')
	reasonable_percent = fields.Float("Reasonable Rent Percentage")
	reasonable_price_per = fields.Float("Reasonable Price Percentage")
	facility_ids = fields.One2many('facility.services.line','property_id')

	def print_service(self):
		return self.env.ref('property_rental_mgt_app.facility_services_report_as_pdf').report_action(self)


	# Calc price of size
	@api.depends('maintain_charge')
	def calc_price_of_size(self):
		pz = self.env['property.size'].search([])
		for rec in self:
			rec.maintain_charge = rec.area * pz.price

	@api.onchange('area')
	def onchange_area(self):
		pz = self.env['property.size'].search([])
		for rec in self:
			rec.maintain_charge = rec.area * pz.price

	def unlink(self):
		for line in self:
			if line.state != 'draft':
				raise UserError(_('You cannot delete Sale And Rent Property (name: %s)') % (line.name,))
		return super(ProductProduct, self).unlink()

	@api.onchange('state_id')
	def get_country(self):
		if self.state_id:
			self.country_id = self.state_id.country_id

	@api.onchange('property_avl_from')
	def culculate_age(self):
		if self.property_avl_from:
			if self.property_avl_from > date.today():
				return {
						 'warning': {'title': 'Warning!', 'message': 'Please enter valid property exist date...!'},
						  'value': {'property_avl_from': None}
						}

			self.age = 0
			self.months = 0
			days_in_year = 365
			year = int((date.today() - self.property_avl_from).days / days_in_year)
			result = relativedelta.relativedelta(fields.Date.today(), self.property_avl_from)
			months = result.months + (12*result.years)
			if year > 0:
				self.age = year
			else:
				self.months = months

	def button_confirm(self):
		if self.state == 'draft' and self.property_book_for == 'sale':
			if self.property_price <= 0 or self.discounted_price <= 0:
				raise UserError(_("Please enter valid property price or reasonable amount...!"))
			self.state = 'sale'
		if self.state == 'draft' and self.property_book_for == 'rent':
			if self.rent_price <= 0 or self.deposite <= 0:
				raise UserError(_("Please enter valid property rent amount...!"))
			contracts = self.env['contract.contract'].search([])
			if not contracts:
				raise UserError(_("Please first create contract type from property configuration -> contract...!"))
			self.state = 'rent'

		if self.user_commission_ids:
			for each in self.user_commission_ids:
				if each.percentage <= 0:
					raise UserError(_("Please enter valid commission percentage in commission lines...!"))

	def button_set_to_draft(self):
		if self.state in ['rent','sale']:
			self.state = 'draft'

	def button_restore(self):
		self.state = 'draft'

	@api.onchange('state')
	def change_state(self):
		if self.renter_history_ids or self.invoice_ids:
			raise UserError(_("You can not move this property(%s) in another state..!")%self.name)
		if self.state == 'sale':
			self.property_book_for = 'sale'
		elif self.state == 'rent':
			self.property_book_for = 'rent'

	@api.onchange('reasonable_percent','reasonable_rent','rent_price')
	def calculate_reasonable_rent(self):
		if self.reasonable_rent:
			if self.reasonable_percent > 0:
				discount = (self.rent_price * self.reasonable_percent)/100
				self.deposite = self.rent_price - discount
			else:
				self.deposite = self.rent_price
		else:
			self.deposite = self.rent_price

	@api.onchange('reasonable_price_per','reasonable_price','property_price')
	def calculate_reasonable_price(self):
		if self.reasonable_price:
			if self.reasonable_price_per > 0:
				discount  = (self.property_price * self.reasonable_price_per)/100
				self.discounted_price = self.property_price - discount
			else:
				self.discounted_price = self.property_price
		else:
			self.discounted_price = self.property_price

	@api.depends()
	def _compute_invoice_count(self):
		for rec in self:
			invoices = self.env['account.move'].search([('property_id','=',rec.id)])
			rec.invoice_count = len(invoices)

	@api.depends()
	def _compute_contract_count(self):
		for rec in self:
			contracts = self.env['contract.details'].search([('property_id','=',rec.id)])
			rec.contract_count = len(contracts)

	@api.depends()
	def _compute_maintanance(self):
		for rec in self:
			maintanance = self.env['property.maintanance'].search([('property_id','=',rec.id)])
			rec.maintain_count = len(maintanance)

	@api.model
	def default_get(self, fields):
		result = super(ProductProduct, self).default_get(fields)
		facility_ids = [(5, 0, 0)]
		reg_obj = self.env['property.facility'].search([])
		for m in reg_obj:
			line = (0, 0, {
				'facility_id': m.id,
			})
			facility_ids.append(line)

		result.update({
			'facility_ids': facility_ids,
		})
		return result



	def buy_now_property(self):
		if self.invoice_ids:
			if any(inv.state =='paid' for inv in self.invoice_ids):
				self.state = 'occ'
		# 		raise UserError(_("This property (%s) already sold out..!")%self.name)
		# if self.property_book_for != 'sale':
		# 	raise UserError(_("This property only allow for Rent..!"))
		# if self.property_price < 1:
		# 	raise UserError(_("Please enter valid property price for (%s)..!") % self.name)
		#
		# view_id = self.env.ref('property_rental_mgt_app.property_buy_wizard')
		# if self.reasonable_price:
		# 	property_price = self.discounted_price
		# else:
		# 	property_price = self.property_price
		# if view_id:
		# 	buy_property_data = {
		# 		'name' : _('Purchase Property & Partial Payment'),
		# 		'type' : 'ir.actions.act_window',
		# 		'view_type' : 'form',
		# 		'view_mode' : 'form',
		# 		'res_model' : 'property.buy',
		# 		'view_id' : view_id.id,
		# 		'target' : 'new',
		# 		'context' : {
		# 					'property_id' : self.id,
		# 					'desc' : self.description,
		# 					'property_price':property_price,
		# 					'owner_id':self.owner_id.id,
		# 					'purchaser_id':self.env.user.partner_id.id,
		# 					 },
		# 	}
		# return buy_property_data

	def reserve_property(self):
		if self.renter_history_ids:
			if all(each.state =='reserve' for each in self.renter_history_ids):
				raise UserError(_("This property already reserved..!"))

		if self.property_book_for != 'rent':
			raise UserError(_("This property only allow for sale..!"))
		if self.rent_price <= 0 or self.deposite <= 0:
			raise UserError(_("Please enter valid property rent or deposite price for (%s)..!") % self.name)
		view_id = self.env.ref('property_rental_mgt_app.property_book_wizard')

		if view_id:
			book_property_data = {
				'name' : _('Reserve Property & Contract Configure'),
				'type' : 'ir.actions.act_window',
				'view_type' : 'form',
				'view_mode' : 'form',
				'res_model' : 'property.book',
				'view_id' : view_id.id,
				'target' : 'new',
				'context' : {
							'property_id' :self.id,
							'desc' : self.description,
							'rent_price':self.rent_price,
							'renter_id':self.user_id.id or self.env.user.id,
							'owner_id':self.owner_id.id,
							'deposite':self.deposite,
							 },
			}
		return book_property_data

	def action_view_invoice(self):
		for rec in self:
			invoices = self.env['account.move'].search([('property_id','=',rec.id)])
			action = self.env.ref('account.action_move_out_invoice_type').read()[0]
			if len(invoices) > 1:
				action['domain'] = [('id', 'in', invoices.ids)]
			elif len(invoices) == 1:
				action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
				action['res_id'] = invoices.ids[0]
			else:
				action = {'type': 'ir.actions.act_window_close'}
			return action


	def action_view_maintenance(self):
		for rec in self:
			invoices = self.env['property.maintanance'].search([('property_id','=',rec.id)])
			action = self.env.ref('property_rental_mgt_app.action_maintanance').read()[0]
			if len(invoices) > 1:
				action['domain'] = [('id', 'in', invoices.ids)]
			elif len(invoices) == 1:
				action['views'] = [(self.env.ref('property_rental_mgt_app.property_maintanance_form').id, 'form')]
				action['res_id'] = invoices.ids[0]
			else:
				action = {'type': 'ir.actions.act_window_close'}
			return action


	# automatically set property to rentable state
	def property_set_to_available(self):
		contracts = self.env['contract.details'].search([('property_id','=',self.id)])
		if all(c.state == "expire" for c in contracts):
			self.write({'state':"rent"})

	def property_set_to_under_maintenance(self):
		for rec in self:
			rec.state = 'under_maintenance'

	def create_maintain_charge_invoice(self):
		inv_obj = self.env['account.move'].search([])
		vals = {
			'property_id': self.id,
			'move_type': 'out_invoice',
			'invoice_origin': self.name,
			'partner_id': self.owner_id.id,
			'invoice_date': self.property_avl_from,
			'invoice_line_ids': [(0, 0, {
				'name': "Maintain Charge Fee",
				'product_id': self.id,
				'price_unit': self.maintain_charge})],
		}
		invoice = inv_obj.create(vals)
		return invoice

class FacilityServicesLine(models.Model):
	_name = 'facility.services.line'

	facility_id = fields.Many2one('property.facility', required=True, store=True)
	count = fields.Integer(string="Count", required=True)
	is_exist = fields.Boolean(string="Existing ?", required=True)
	#flour = fields.Char(related="facility_id.flour")
	property_id = fields.Many2one('product.product')


	@api.onchange('is_exist')
	def set_count_to_zero_for_facility_when_not_exist(self):
		for rec in self:
			if not rec.is_exist:
				rec.count = 0


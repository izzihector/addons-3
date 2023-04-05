from odoo import _, api, fields, models
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
# from .hijri_converter import convert
from num2words import num2words
from odoo.exceptions import ValidationError
from datetime import date

class ProductProperty(models.Model):
    _inherit = 'product.product'

    avg = fields.Float(compute="get_avg",string='Administrative fees')
    

    def action_done(self):
        for rec in self:
            rec.state = 'occ'

    
    @api.depends('avg')
    def get_avg(self):
        for rec in self:
            if rec.property_book_for == 'rent':
                if rec.reasonable_rent == True:
                    rec.avg = rec.deposite * 5 / 100
                if  rec.reasonable_rent == False:
                    rec.avg = rec.deposite * 5 / 100

            if rec.property_book_for == 'sale':
                if rec.reasonable_price == True:
                    rec.avg = rec.discounted_price * 5 / 100
                if  rec.reasonable_price == False:
                    rec.avg = rec.discounted_price * 5 / 100
                    
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
                            'avg' : self.avg,
                            'club_fees' : self.club_fees,
                            'diesel_fees' : self.diesel_fees,
                            # 'warranty' : self.warranty,
							'renter_id':self.user_id.id or self.env.user.id,
							'owner_id':self.owner_id.id,
							'deposite':self.deposite,
							# 'facility_ids':self.facility_ids.ids,
                            },
			}
	    return book_property_data


class RenterHistory(models.Model):
    _inherit = 'renter.history'
    
    avg = fields.Float(string="Admin fees")
    total_administrative_fees = fields.Float(string="Total admin fees")
    warranty = fields.Float(string="Deposite")
    club_fees = fields.Float(string="Gym")
    diesel_fees = fields.Float(string="Diesel")

    def create_rent_invoice(self):
        account_inv_obj = self.env['account.move']
        product_id = self.property_id
        # Search for the income account
        if product_id.property_account_income_id:
            income_account = product_id.property_account_expense_id.id
        elif product_id.categ_id.property_account_income_categ_id:
            income_account = product_id.categ_id.property_account_income_categ_id.id
        else:
            raise UserError(_('Please define income '
                              'account for this product: "%s" (id:%d).')
                            % (product_id.name, product_id.id))
        if self.total_administrative_fees == 0:
            vals  = {
                'property_id':self.property_id.id,
                'move_type': 'out_invoice',
                'invoice_origin':self.property_id.name,
                'partner_id': self.owner_id.id,
                'invoice_user_id':self.renter_id.id or self.property_id.salesperson_id.id,
                'invoice_line_ids': [(0,0,{
                    'name':self.property_id.name,
                    'product_id':self.property_id.id,
                    'account_id': income_account,
                    'price_unit': self.deposite})], 
                }
        else:
            acc_obj = self.env['account.account'].search([('use_for_discount','=', True)])
            vals  = {
                'property_id':self.property_id.id,
                'move_type': 'out_invoice',
                'invoice_origin':self.property_id.name,
                'partner_id': self.owner_id.id,
                'invoice_user_id':self.renter_id.id or self.property_id.salesperson_id.id,
                'invoice_line_ids': [(0,0,{
                    'name':self.property_id.name,
                    'product_id':self.property_id.id,
                    'account_id': acc_obj,
                    'price_unit': self.total_administrative_fees})],
                }

        # if self.rent_price <= 0 or self.avg <= 0:
        #     raise UserError(_("You will not buy this property, (%s) because this property price is zero.") % self.property_id.name)

        invoice_id = account_inv_obj.create(vals)
        if invoice_id:
            self.write({'invoice_id':invoice_id.id, 'state':'reserve','is_invoice':True})

        return {
            'name': 'Partial Payment Invoice',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_id':invoice_id.id,
            'views': [(self.env.ref('account.view_move_form').id, 'form')],
            'res_model': 'account.move',
            'domain': [('id','=',invoice_id.id)],
        }
    
class PropertyInhBook(models.TransientModel):
    _inherit = 'property.book'

    avg = fields.Float(string="Administrative fees")
    total_administrative_fees = fields.Float('Total administrative fees')
    warranty = fields.Float(string="Deposite")
    club_fees = fields.Float(string="Gym")
    diesel_fees = fields.Float(string="Diesel")

    @api.onchange('contract_id')
    def get_month_deposite(self):
        if self.contract_id:
            if self.contract_id.contract_type == 'monthly':
                self.contract_month = self.contract_id.month
            if self.contract_id.contract_type == 'yearly':
                self.contract_month = self.contract_id.year * 12
            self.deposite_amount = self.contract_month * self.deposite
            self.total_administrative_fees = self.avg * self.contract_month
            self.total_deposite = self.deposite_amount
            self.month = self.contract_month
        # This Is Calculation Section
    def create_rent_contract(self):
        if self.from_date == fields.Date.today():
            state = 'running'
        else:
            state = 'new'
        contract_id = self.env['contract.details'].create({'club_fees':self.club_fees,'diesel_fees':self.diesel_fees,'contract_month':self.month,'deposite':self.deposite_amount,'renewal_date':self.renewal_date,'rent_price':self.property_id.rent_price,'contract_id':self.contract_id.id,'owner_id':self.owner_id.id,'renewal_date':self.renewal_date,'partner_id':self.renter_id.id,'warranty':self.warranty,'property_id':self.property_id.id,'date':fields.Date.today(), 'from_date':self.from_date, 'to_date':self.to_date,'state':state})
        if contract_id:  
            self.property_id.write({'renter_history_ids':[(0,0,{
                'contract_month':self.month,
                'deposite':self.deposite_amount,
                'reference':self.contract_id.name,
                'property_id':self.property_id.id,
                'owner_id':self.owner_id.id, 
                'state':self.state, 
                'warranty':self.warranty,
                'rent_price':self.rent_price, 
                'renter_id':self.renter_id.id, 
                'date':fields.Date.today(), 
                'from_date':self.from_date, 
                'to_date':self.to_date, 
                'property_id':self.property_id.id,
                'contract_id': contract_id.id,

            })]})

            # self.property_id.write({'renter_history_ids':[(0,0,{
            #     'contract_month':self.month,
            #     'deposite':self.total_administrative_fees,
            #     'reference':self.contract_id.name,
            #     'property_id':self.property_id.id,
            #     'owner_id':self.owner_id.id,
            #     'state':self.state,
            #     'warranty':self.warranty,
            #     'total_administrative_fees': self.total_administrative_fees,
            #     'renter_id':self.renter_id.id,
            #     'date':fields.Date.today(),
            #     'from_date':self.from_date,
            #     'to_date':self.to_date,
            #     'property_id':self.property_id.id,
            #     'contract_id': contract_id.id,
            #     'club_fees': self.club_fees,
            #     'diesel_fees': self.diesel_fees
            # })]})
            #
            
            self.property_id.write({'state':'reserve','is_reserved':True,'user_id':self.env.user.id})
            template_id =  self.env.ref('property_rental_mgt_app.property_reserved_template')
            values = template_id.generate_email(self.id, ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to', 'scheduled_date'])
            mail_mail_obj = self.env['mail.mail']
            msg_id = mail_mail_obj.sudo().create(values)
            if msg_id:
                mail_mail_obj.sudo().send(msg_id)
 
        return {
            'name': 'Contract Details',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_id':contract_id.id,
            'views': [(self.env.ref('property_rental_mgt_app.property_contract_details_form').id, 'form')],
            'res_model': 'contract.details',
            'domain': [('invoice_id','=',self.property_id.id)],
        }

    @api.model
    def default_get(self,default_fields):
        res = super(PropertyInhBook, self).default_get(default_fields)
        ctx = self._context
        property_data = {
            'deposite_amount':ctx.get('deposite'),
            'property_id':ctx.get('property_id'),
            'desc':ctx.get('desc'),
            'rent_price':ctx.get('rent_price'),
            'renter_id':ctx.get('renter_id'),
            'owner_id':ctx.get('owner_id'),
            'avg':ctx.get('avg'),
            'warranty':ctx.get('warranty'),
            'deposite':ctx.get('deposite'),
            'club_fees':ctx.get('club_fees'),
            'diesel_fees':ctx.get('diesel_fees')
            # 'facility_ids':ctx.get('facility_ids')
        }
        res.update(property_data)
        return res
    
   

class ContractDetails(models.Model):
    _inherit = 'contract.details'


    warranty = fields.Float(string="Deposite")
    club_fees = fields.Float(string="Gym")
    diesel_fees = fields.Float(string="Diesel")
    # facility_ids = fields.One2many('property.facility','id')
    contract_template_id = fields.Many2one('contract.template', string='Contract Template')
    template_content = fields.Html()

    def print_contract(self):

        return self.env.ref('property.action_report_contract_appendix').report_action(self)
    

class AccountAccount(models.Model):
    _inherit = 'account.account'

    use_for_discount = fields.Boolean(string="Is Discount")

    

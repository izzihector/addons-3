from odoo import fields, models, api


class PropertySize(models.Model):
    _name = 'property.size'
    _description = 'Description'

    name = fields.Char()
    price = fields.Float("Price")

class FacilityCategory(models.Model):
    _name = 'facility.category'

    name = fields.Char(string="Category Of Facility")


class PropertyFacility(models.Model):
    _name = 'property.facility'
    _description = 'Property Facility Service'

    name = fields.Char("Name", required=True)
    brand = fields.Char(string="Brand")
    disc = fields.Char(string="Description")
    categ_id = fields.Many2one('facility.category',string="Category",required=True)

class AkCurrentLiabilitiesAddedToAccountPayment(models.Model):
    _inherit = 'account.payment'

    destination_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Destination Account',
        store=True, readonly=False,
        compute='_compute_destination_account_id',
        domain="[('user_type_id.type', 'in', ('receivable', 'payable', 'other')), ('company_id', '=', company_id)]",
        check_company=True)

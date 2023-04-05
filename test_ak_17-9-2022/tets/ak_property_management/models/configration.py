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

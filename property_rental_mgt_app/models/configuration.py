# -*- coding: utf-8 -*-
from random import randint
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class FacilityCategory(models.Model):
    _name = 'facility.category'

    name = fields.Char(string="Category Of Facility")

# class PropertyNames(models.Model):
#     _name = 'property.names'
#
#     name = fields.Char(string="Property")

class PropertyFacility(models.Model):
    _name = 'property.facility'
    _description = 'Property Facility Service'

    def _get_default_color(self):
        return randint(1, 11)

    color = fields.Integer(string='Color Index', default=_get_default_color)
    name = fields.Char("Name", required=True)
    categ_id = fields.Many2one('facility.category',string="Category",required=True)
    #flour = fields.Char(string="Flour")



class PartialPayment(models.Model):
    _name = 'partial.payment'
    _description = 'Partial Payment'

    name = fields.Char("Name", required=True)
    number_of_pay = fields.Integer("#Partial Payment", required=True)

    @api.model
    def create(self, vals):
        if vals['number_of_pay'] <= 0:
            raise UserError(_("Please enter valid # Payments"))
        res = super(PartialPayment, self).create(vals)
        return res


class PropertyType(models.Model):
    _name = 'property.type'
    _description = 'Property Type'

    name = fields.Char("Name", required=True)

class PropertySize(models.Model):
    _name = 'property.size'
    _description = 'Property Size Price'

    name = fields.Char("Unit", required=True)
    price = fields.Float("Price")


# class MaintenanceStage(models.Model):
#     """ Model for case stages. This models the main stages of a Maintenance Request management flow. """
#     _name = 'maintenance.stage'
#     _description = 'Maintenance Stage'
#     _order = 'sequence, id'
#
#     name = fields.Char('Name', required=True, translate=True)
#     sequence = fields.Integer('Sequence', default=20)
#     fold = fields.Boolean('Folded in Maintenance Pipe')
#     done = fields.Boolean('Request Done')


class DieselPricing(models.Model):
    _name = 'diesel.pricing'
    _description = 'Price  Of Diesel'

    name = fields.Char("Standard", required=True)
    price = fields.Float("Price")

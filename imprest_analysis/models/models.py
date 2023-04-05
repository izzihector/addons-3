# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning, UserError,ValidationError
from calendar import monthrange
import time
import math
from odoo.tools import float_round


class imprest_analysis(models.Model):
    _name = 'imprest.analysis'
    _description = 'Imprest Analysis'
    _inherit = ['mail.thread']

    state = [
        ('draft', 'Draft'),
        ('submitted', 'Waiting For Manager Approval'),
        ('confirm', 'Confirm'),
        ('post', 'Posted'),
        ('reject', "Rejected")
    ]

    name = fields.Char("Number", required=True, index=True, default=lambda self: _('New'), copy=False)
    description = fields.Text("Description")
    employee_id = fields.Many2one("hr.employee", string="Employee")
    journal_id = fields.Many2one("account.journal", string="Payment Journal",domain=[('type','in',['cash','bank'])])
    date = fields.Date("Date")
    amount = fields.Float("Amount")
    amount_char = fields.Text("Amount(Character)", compute="compute_char_amount", store=True)
    state = fields.Selection(state, string="State", required=True, default="draft", index=True,track_visibility='onchange')
    move_id = fields.Many2one('account.move', 'Journal Entry', readonly=True)
    currency_id = fields.Many2one('res.currency', 'Currency',default=lambda self: self.env.user.company_id.currency_id.id)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env['res.company']._company_default_get('imprest.analysis'))

    line_ids = fields.One2many(comodel_name="imprest.analysis.line", inverse_name="imprest_id", string="Imprest Lines",
                               states={'post': [('readonly', True)]},)

    @api.depends('line_ids.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.line_ids:
                line._compute_amount()
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
            })

    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all',tracking=True)
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('imprest.imprest') or 'New'
        result = super(imprest_analysis, self).create(vals)
        return result

    def button_submit(self):
        self.state = "submitted"

    def confirm(self):
        self.state = "confirm"

    def reject(self):
        self.state = "reject"

    def post(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        imprest = self.env['imprest.analysis'].browse(active_ids)

        journal = self.journal_id
        credit_line = debit_line = []
        ctx = dict(self._context)
        for rec in self.line_ids:
            if len(rec.account_id) < 1:
                raise ValidationError("Please select account!")

        move = self.env['account.move'].create({
            'journal_id': journal.id,
            'ref': self.description,
            'date': self.date,
            'imprest_id': imprest.id,

        })

        AccountMoveLine = self.env['account.move.line'].with_context(check_move_validity=False)

        AccountMoveLine.create({
            'name': imprest.name,
            'move_id': move.id,
            'account_id': self.journal_id.payment_credit_account_id.id,
            'amount_currency': self.amount_total,
            'currency_id': self.currency_id.id,
            'credit': self.amount_total,
            'date': self.date
        })

        for line in self.line_ids:
            taxes = line.taxes_id.with_context(round=True).compute_all(line.price_unit, line.currency_id, 1, False)
            amount = taxes['total_excluded']

            move_line = {
                'name': line.name,
                'move_id': move.id,
                'account_id': line.account_id.id,
                'amount_currency': line.price_unit,
                'currency_id': self.currency_id.id,
                'debit': line.price_unit if line.price_unit > 0 else 0,
                'credit': 0,
                'tax_ids': line.taxes_id.ids if line.taxes_id else False,
                'analytic_account_id': line.analytic_id.id if line.analytic_id else False,
                'partner_id': line.partner_id.id if line.partner_id else False,
                'date': line.date
            }
            AccountMoveLine.create(move_line)
            for tax in taxes['taxes']:
                amount = tax['amount']
                if tax['tax_repartition_line_id']:
                    rep_ln = self.env['account.tax.repartition.line'].browse(tax['tax_repartition_line_id'])
                    # base_amount = self.env['account.move']._get_base_amount_to_display(tax['base'], rep_ln)
                    base_amount = amount
                else:
                    base_amount = None

                move_line_tax_values = {
                    'name': tax['name'],
                    'move_id': move.id,
                    'quantity': 1,
                    'date': line.date,
                    'amount_currency': amount,
                    'currency_id': self.currency_id.id,
                    'debit': amount if amount > 0 else 0,
                    'credit': -amount if amount < 0 else 0,
                    'account_id': tax['account_id'],
                    'tax_repartition_line_id': tax['tax_repartition_line_id'],
                    'tax_base_amount': base_amount,

                }
                AccountMoveLine.create(move_line_tax_values)
        move.post()
        self.move_id = move.id
        self.state = "post"

    def button_set_Draft(self):
        self.state = "draft"

    def button_journal(self):
        return {
            'name': _('Journal Entry'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', '=', self.move_id.id)],
        }

    def unlink(self):
        if self.state != 'draft':
            raise UserError("You cannot delete this Record. Only DRAFT records can be deleted.")
        return super(imprest_analysis, self).unlink()


class imprest_analysis_line(models.Model):
    _name = 'imprest.analysis.line'
    _description = 'Imprest Analysis Line'

    imprest_id = fields.Many2one("imprest.analysis", string="Imprest")
    type = fields.Selection([('bill', 'Bill'), ('other', 'Other')], default= 'bill')
    date = fields.Date("Date")
    name = fields.Text("Description", required=True)
    partner_id = fields.Many2one('res.partner')
    beneficiary = fields.Text("Beneficiary")
    account_id = fields.Many2one('account.account')
    analytic_id = fields.Many2one("account.analytic.account", string="Analytic Account")
    price_unit = fields.Float("Amount")
    taxes_id = fields.Many2many('account.tax', string='Taxes',domain=['|', ('active', '=', False), ('active', '=', True)])
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)
    company_id = fields.Many2one('res.company', related='imprest_id.company_id', string='Company', store=True,readonly=True)
    currency_id = fields.Many2one(related='imprest_id.currency_id', store=True, string='Currency', readonly=True)
    state = fields.Selection(related='imprest_id.state', store=True, readonly=False)


    @api.depends('price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            taxes = line.taxes_id.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                )
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    def _prepare_compute_all_values(self):

        self.ensure_one()
        return {
            'price_unit': self.price_unit,
            'currency_id': self.imprest_id.currency_id,
        }
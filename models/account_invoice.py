# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    origin_purchase = fields.Many2many(
    'purchase.order', string='Purchase Order',
    compute='_get_purchase_order', readonly=True,
    store=True)

    @api.one
    @api.depends('origin')
    def _get_purchase_order(self):
            bill_origin = self.origin
            if bill_origin != False:
                polist = bill_origin.split(",")
                purchase = self.env['purchase.order'].search([('name','in',polist)])
                self.origin_purchase = purchase or False

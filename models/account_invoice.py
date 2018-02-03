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

    @api.onchange('state', 'partner_id', 'invoice_line_ids')
    def _onchange_allowed_purchase_ids(self):
        '''
        The purpose of the method is to define a domain for the available
        purchase orders.
        '''
        result = {}

        # A PO can be selected only if at least one PO line is not already in the invoice
        purchase_line_ids = self.invoice_line_ids.mapped('purchase_line_id')
        purchase_ids = self.invoice_line_ids.mapped('purchase_id').filtered(lambda r: r.order_line <= purchase_line_ids)

        #modified the method to allow client to choose any PO for that specific vendor.
        result['domain'] = {'purchase_id': [
            ('state', 'in', ['purchase','done']),
            ('partner_id', 'child_of', self.partner_id.id),
            ('id', 'not in', purchase_ids.ids),
            ]}
        return result

    @api.multi
    @api.onchange('partner_id')
    def _add_credit_line(self):
        for record in self:
            if record.type in ['out_refund','in_refund']:
                lines = record.invoice_line_ids
                new_lines = record.env['account.invoice.line']
                data = {
                    'name': '*Credit*',
                    'product_id': 10656,
                    'quantity': 1,
                    'account_id':17,
                }
                new_line = new_lines.new(data)
                new_lines += new_line
                record.invoice_line_ids += new_lines

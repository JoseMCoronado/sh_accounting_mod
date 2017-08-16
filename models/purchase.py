# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends('state', 'order_line.qty_invoiced', 'order_line.qty_received', 'order_line.product_qty')
    def _get_invoiced(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for order in self:
            if order.state not in ('purchase', 'done'):
                order.invoice_status = 'no'
                continue

            if any(line.qty_invoiced > 0 for line in order.order_line):
                order.invoice_status = 'invoiced'
            elif all(line.qty_invoiced == 0 for line in order.order_line):
                order.invoice_status = 'to invoice'    
            else:
                order.invoice_status = 'no'

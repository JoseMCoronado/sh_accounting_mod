# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError
import json

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    origin_purchase = fields.Many2many(
    'purchase.order', string='Purchase Order',
    compute='_get_purchase_order', readonly=True,
    store=True)

    @api.multi
    def action_send_bill(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'account.invoice',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'default_partner_ids': [(6,0,[self.partner_id.id])]
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


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
    def print_payments(self):
        for record in self:
            json1_data = json.loads(record.payments_widget)
            print json1_data
            return json1_data

    @api.multi
    @api.onchange('partner_id')
    def _add_credit_line(self):
        for record in self:
            if record.type in ['out_refund','in_refund']:
                lines = record.invoice_line_ids
                new_lines = record.env['account.invoice.line']
                if record.type == 'in_refund':
                    product = 11101
                    account = 19
                else:
                    product = 10656
                    account = 17
                data = {
                    'name': '*Credit*',
                    'product_id': product,
                    'quantity': 1,
                    'account_id':account,
                }
                new_line = new_lines.new(data)
                new_lines += new_line
                record.invoice_line_ids += new_lines

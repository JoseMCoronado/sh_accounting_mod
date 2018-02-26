# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class account_payment(models.Model):
    _inherit = "account.payment"

    invoice_due_date = fields.Datetime(string='Bill Due Date',
    compute='_get_due_date', readonly=True,
    store=True)

    @api.multi
    @api.depends('invoice_ids')
    def _get_due_date(self):
            for pay in self:
                if pay.invoice_ids:
                    pay.invoice_due_date = pay.invoice_ids[0].date_due

    @api.multi
    def post(self):
        super(account_payment, self).post()
        if self.payment_type == 'outbound' and self.partner_type == 'supplier' and self.payment_method_id == self.env.ref('account.account_payment_method_manual_out'):
            self.state = 'sent'

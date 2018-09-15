# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}
# Since invoice amounts are unsigned, this is how we know if money comes in or goes out
MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'in_refund': 1,
    'in_invoice': -1,
    'out_refund': -1,
}


class account_payment(models.Model):
    _inherit = "account.payment"

    invoice_due_date = fields.Datetime(string='Bill Due Date',
    compute='_get_due_date', readonly=True,
    store=True)
    payment_sh_type = fields.Selection([
        ('Check', 'Check'),
        ('Credit Card', 'Credit Card'),
        ('Wire Transfer', 'Wire Transfer'),
        ('Cash', 'Cash'),
        ], string='Payment Type', default="Check",copy=False)
    customer_check_number = fields.Char(string="Customer Check Number")

    @api.onchange('payment_sh_type','customer_check_number')
    def set_memo(self):
            for record in self:
                if record.partner_type != 'supplier':
                    if record.communication:
                        parsed_desc = record.communication.split("|")
                    else:
                        parsed_desc = ['']
                    string = "|"
                    if record.payment_sh_type:
                        string += '%s ' % (record.payment_sh_type)
                    if record.customer_check_number:
                        string += '%s' % (record.customer_check_number)
                    new_desc = str(parsed_desc[0]) + string
                    record.communication = new_desc


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

class account_register_payments(models.TransientModel):
    _inherit = "account.register.payments"

    payment_sh_type = fields.Selection([
        ('Check', 'Check'),
        ('Credit Card', 'Credit Card'),
        ('Wire Transfer', 'Wire Transfer'),
        ('Cash', 'Cash'),
        ], string='Payment Type', default="Check",copy=False)
    customer_check_number = fields.Char(string="Customer Check Number")

    @api.onchange('payment_sh_type','customer_check_number')
    def set_memo(self):
            for record in self:
                if record.partner_type != 'supplier':
                    if record.communication:
                        parsed_desc = record.communication.split("|")
                    else:
                        parsed_desc = ['']
                    string = "|"
                    if record.payment_sh_type:
                        string += '%s ' % (record.payment_sh_type)
                    if record.customer_check_number:
                        string += '%s' % (record.customer_check_number)
                    new_desc = str(parsed_desc[0]) + string
                    record.communication = new_desc

    def get_payment_vals(self):
        """ Hook for extension """
        return {
            'journal_id': self.journal_id.id,
            'payment_method_id': self.payment_method_id.id,
            'payment_date': self.payment_date,
            'communication': self.communication,
            'invoice_ids': [(4, inv.id, None) for inv in self._get_invoices()],
            'payment_type': self.payment_type,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_type': self.partner_type,
            'payment_sh_type': self.payment_sh_type,
            'customer_check_number': self.customer_check_number,
        }

    @api.model
    def default_get(self, fields):
        rec = super(account_register_payments, self).default_get(fields)
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')

        # Checks on context parameters
        if not active_model or not active_ids:
            raise UserError(_("Programmation error: wizard action executed without active_model or active_ids in context."))
        if active_model != 'account.invoice':
            raise UserError(_("Programmation error: the expected model for this action is 'account.invoice'. The provided one is '%d'.") % active_model)

        # Checks on received invoice records
        invoices = self.env[active_model].browse(active_ids)
        if any(invoice.state != 'open' for invoice in invoices):
            raise UserError(_("You can only register payments for open invoices"))
        if any(inv.commercial_partner_id != invoices[0].commercial_partner_id for inv in invoices):
            raise UserError(_("In order to pay multiple invoices at once, they must belong to the same commercial partner."))
        if any(MAP_INVOICE_TYPE_PARTNER_TYPE[inv.type] != MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type] for inv in invoices):
            raise UserError(_("You cannot mix customer invoices and vendor bills in a single payment."))
        if any(inv.currency_id != invoices[0].currency_id for inv in invoices):
            raise UserError(_("In order to pay multiple invoices at once, they must use the same currency."))

        total_amount = sum(inv.residual * MAP_INVOICE_TYPE_PAYMENT_SIGN[inv.type] for inv in invoices)
        communication = ' '.join([ref for ref in invoices.mapped('reference') if ref])
        if any(invoice.type in ['out_invoice','out_refund'] for invoice in invoices):
            selected_journal = 10
        else:
            selected_journal = 8
        rec.update({
            'amount': abs(total_amount),
            'currency_id': invoices[0].currency_id.id,
            'payment_type': total_amount > 0 and 'inbound' or 'outbound',
            'partner_id': invoices[0].commercial_partner_id.id,
            'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
            'communication': communication,
            'journal_id': selected_journal,
        })
        return rec

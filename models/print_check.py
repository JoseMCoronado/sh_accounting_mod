from odoo import addons, models, fields, api, _
from odoo.osv import osv
from odoo.report import report_sxw
from odoo.tools.translate import _

class ExtendedSession(addons.l10n_us_check_printing.report.print_check.report_print_check):

    def make_stub_line_two(self, payment, invoice):
        """ Return the dict used to display an invoice/refund in the stub
        """
        # Find the account.partial.reconcile which are common to the invoice and the payment
        if invoice.type in ['in_invoice', 'out_refund']:
            invoice_sign = 1
            invoice_payment_reconcile = invoice.move_id.line_ids.mapped('matched_debit_ids').filtered(lambda r: r.debit_move_id in payment.move_line_ids)
        else:
            invoice_sign = -1
            invoice_payment_reconcile = invoice.move_id.line_ids.mapped('matched_credit_ids').filtered(lambda r: r.credit_move_id in payment.move_line_ids)

        if payment.currency_id != payment.journal_id.company_id.currency_id:
            amount_paid = abs(sum(invoice_payment_reconcile.mapped('amount_currency')))
        else:
            amount_paid = abs(sum(invoice_payment_reconcile.mapped('amount')))

        return {
            'due_date': invoice.date_due,
            'number': invoice.reference and invoice.number + ' - ' + invoice.reference or invoice.number,
            'reference': invoice.reference,
            'origin': invoice.origin,
            'amount_total': invoice_sign * invoice.amount_total,
            'amount_residual': invoice_sign * invoice.residual,
            'amount_paid': invoice_sign * amount_paid,
            'currency': invoice.currency_id,
    }

report.print_check.make_stub_line = make_stub_line_two

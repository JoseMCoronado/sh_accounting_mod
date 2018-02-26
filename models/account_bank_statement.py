# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class BankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    @api.multi
    def button_cancel_reconciliation(self):
        moves_to_cancel = self.env['account.move']
        payment_to_unreconcile = self.env['account.payment']
        payment_to_cancel = self.env['account.payment']
        for st_line in self:
            moves_to_unbind = st_line.journal_entry_ids
            for move in st_line.journal_entry_ids:
                for line in move.line_ids:
                    payment_to_unreconcile |= line.payment_id
                    if st_line.move_name and line.payment_id.payment_reference == st_line.move_name:
                        #there can be several moves linked to a statement line but maximum one created by the line itself
                        moves_to_cancel |= move
                        payment_to_cancel |= line.payment_id

            moves_to_unbind = moves_to_unbind - moves_to_cancel

            if moves_to_unbind:
                moves_to_unbind.write({'statement_line_id': False})
                for move in moves_to_unbind:
                    move.line_ids.filtered(lambda x: x.statement_id == st_line.statement_id).write({'statement_id': False})

        payment_to_unreconcile = payment_to_unreconcile - payment_to_cancel
        if payment_to_unreconcile:
            payment_to_unreconcile.unreconcile()

        if moves_to_cancel:
            for move in moves_to_cancel:
                move.line_ids.remove_move_reconcile()
            moves_to_cancel.button_cancel()
            moves_to_cancel.unlink()
            self.move_name = False
        if payment_to_cancel:
            payment_to_cancel.unlink()
            self.move_name = False

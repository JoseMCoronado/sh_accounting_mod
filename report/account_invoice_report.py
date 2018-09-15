# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError

class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    parent_categ_id = fields.Many2one('product.category', string='Parent Category')

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ", sub.parent_categ_id as parent_categ_id"

    def _sub_select(self):
        return super(AccountInvoiceReport, self)._sub_select() + ", pt.parent_categ_id as parent_categ_id"

    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + ", pt.parent_categ_id"

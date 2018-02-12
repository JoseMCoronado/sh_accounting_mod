# -*- coding: utf-8 -*-

from ast import literal_eval
from operator import itemgetter
import time

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP

class ResPartner(models.Model):
    _inherit = "res.partner"

    credit_count = fields.Integer(string='Credits',compute='_get_credit_count',readonly=True,store=False)

    @api.multi
    def _get_credit_count(self):
        for record in self:
            credits = record.env['account.invoice'].search([('partner_id','=',record.id),('state','in',('draft', 'open')),('type','=','out_refund')])
            record.credit_count = len(credits)

    def open_partner_history(self):
        action = self.env.ref('account.action_invoice_refund_out_tree').read()[0]
        action['domain'] = literal_eval(action['domain'])
        action['domain'].append(('partner_id', 'child_of', self.ids))
        return action

    def create_credit(self):
        if self.supplier = True:
            action = self.env.ref('sh_accounting_mod.account_action_credit_memo').read()[0]
            salejournals = self.env['account.journal'].search([('type','=','purchase')]).ids
            action['context'] = {
                'default_partner_id':self.id,
                'default_invoice_type':'in_refund',
                'default_type':'in_refund',
                'default_payment_term_id':False,
                'default_journal_id': salejournals[0],
            }
        else:
            action = self.env.ref('sh_accounting_mod.account_action_credit_memo').read()[0]
            salejournals = self.env['account.journal'].search([('type','=','sale')]).ids
            action['context'] = {
                'default_partner_id':self.id,
                'default_invoice_type':'out_refund',
                'default_type':'out_refund',
                'default_payment_term_id':False,
                'default_journal_id': salejournals[0],
            }
        return action

    @api.multi
    def open_outstanding_credits(self):
        for record in self:
            action_data = record.env.ref('sh_accounting_mod.action_outstanding_credits').read()[0]
            action_data.update({'domain':[('partner_id','=',record.id),('state','in',('draft', 'open')),('type','=','out_refund')],'context':{'default_type':'out_refund','default_partner_id':record.id}})
            return action_data

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


    def open_partner_history(self):
        action = self.env.ref('account.action_invoice_refund_out_tree').read()[0]
        action['domain'] = literal_eval(action['domain'])
        action['domain'].append(('partner_id', 'child_of', self.ids))
        return action

    def create_credit(self):
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

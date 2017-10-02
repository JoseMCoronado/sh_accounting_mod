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
        new_list = self.ids + self.commercial_partner_id.child_ids.ids
        action['domain'].append(('partner_id','in',new_list))
        return action

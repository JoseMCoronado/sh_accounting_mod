# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP

class ProductTemplate(models.Model):
    _inherit = "product.template"

    parent_categ_id = fields.Many2one('product.category',string="Parent Category",related="categ_id.parent_id",store=True)

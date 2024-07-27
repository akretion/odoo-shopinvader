# Copyright 2017 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderProduct(models.Model):
    _inherit = "shopinvader.product"

    sale_ok_policy = fields.Selection(selection=[("accept_order", "Accept order"), ("refuse_order", "Refuse order")], string="Sale ok policy")
    in_stock_delay = fields.Char()
    out_of_stock_delay = fields.Char()

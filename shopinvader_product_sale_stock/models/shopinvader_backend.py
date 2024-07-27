# Copyright 2018 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    default_sale_ok_policy = fields.Selection(selection=[("accept_order", "Accept order"), ("refuse_order", "Refuse order")], string="Default sale ok policy", required=True)

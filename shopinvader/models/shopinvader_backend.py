# Copyright 2023 Akretion (http://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>

from odoo import api, fields, models


class ShopinvaderBackend(models.Model):
    _name = "shopinvader.backend"
    _inherit = [
        "server.env.techname.mixin",
        "server.env.mixin",
    ]
    _description = "Shopinvader Backend"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        default=lambda s: s._default_company_id(),
    )

    @api.model
    def _default_company_id(self):
        return self.env.company

# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    univers_ids = fields.Many2many(
        comodel_name="product.category",
        string="Univers",
        domain=[("univers", "=", True)],
    )

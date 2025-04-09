# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    univers = fields.Boolean()
    shopinvader_univers_ids = fields.Many2many(
        "product.category",
        "Shopinvader Univers",
        compute="_compute_univers_category",
    )
    shopinvader_univers_child_ids = fields.Many2many(
        "product.category",
        "Shopinvader Univers Childs",
        compute="_compute_univers_child_category",
    )

    @api.depends_context("index_id")
    @api.depends("univers")
    def _compute_univers_child_category(self):
        index_id = self.env.context.get("index_id", False)
        backend_id = self.env["se.index"].browse(index_id).backend_id.id
        for record in self:
            childs = self.env["product.category"]
            if record.univers:
                products = (
                    self.env["product.product"]
                    .search([("univers_ids", "in", record.ids)])
                    .filtered(
                        lambda rec, backend_id=backend_id: backend_id
                        in rec.se_binding_ids.mapped("backend_id").ids
                    )
                )
                categs = products.categ_id._filter_by_index()
                childs = self.search(
                    [("id", "parent_of", categs.ids)]
                )._filter_by_index()
            record.shopinvader_univers_child_ids = childs

    @api.depends_context("index_id")
    @api.depends("child_id", "child_id.se_binding_ids")
    def _compute_univers_category(self):
        univers = self.search([("univers", "=", True)])._filter_by_index()
        index_id = self.env.context.get("index_id", False)
        backend_id = self.env["se.index"].browse(index_id).backend_id.id
        for record in self:
            products = (
                self.env["product.product"]
                .search(
                    [
                        ("categ_id", "child_of", record.id),
                        ("univers_ids", "in", univers.ids),
                    ]
                )
                .filtered(
                    lambda rec, backend_id=backend_id: backend_id
                    in rec.se_binding_ids.mapped("backend_id").ids
                )
            )
            product_univers = products.univers_ids & univers
            record.shopinvader_univers_ids = product_univers

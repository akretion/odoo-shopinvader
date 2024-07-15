# Copyright 2024 Akretion (http://www.akretion.com)
# Olivier Nibart <olivier.nibart@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ShopinvaderVariant(models.Model):
    _inherit = "shopinvader.variant"

    optional_products = fields.Serialized(
        compute="_compute_optional_products", string="Shopinvader Optional Products"
    )

    def _compute_optional_products(self):
        for record in self:
            optional_products = []
            for pt in record.optional_product_ids:
                variants = pt.shopinvader_bind_ids.filtered(
                    lambda x, rec=record: x.backend_id == rec.backend_id
                    and x.lang_id == rec.lang_id
                ).shopinvader_variant_ids
                for variant in variants:
                    optional_products.append(
                        {
                            "name": variant.name,
                            "id": variant.id,
                            "description": variant.description or "",
                            "url_key": variant.url_key,
                            "images": variant.images,
                        }
                    )
            record.optional_products = optional_products

# Copyright 2023 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product.schemas import (
    ProductProduct as BaseProduct,
    ShortProductCategory,
)


class ProductProduct(BaseProduct, extends=True):
    univers: list[ShortProductCategory] = []

    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super().from_product_product(odoo_rec)
        obj.univers = [
            ShortProductCategory.from_product_category(univers)
            for univers in odoo_rec.univers_ids.sorted("level")
        ]
        return obj

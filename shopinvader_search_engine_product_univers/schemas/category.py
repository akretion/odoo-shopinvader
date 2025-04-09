# Copyright 2023 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product.schemas import (
    ProductCategory as BaseCategory,
    ShortProductCategory as BaseShortProductCategory,
)


class ProductCategory(BaseCategory, extends=True):
    is_univers: bool = False
    univers: list[BaseShortProductCategory] = []

    @classmethod
    def from_product_category(cls, odoo_rec):
        obj = super().from_product_category(odoo_rec)
        obj.is_univers = odoo_rec.univers
        obj.univers = [
            BaseShortProductCategory.from_product_category(univers)
            for univers in odoo_rec.shopinvader_univers_ids
        ]
        return obj


class ShortProductCategory(BaseShortProductCategory, extends=True):
    @classmethod
    def from_product_category(cls, odoo_rec, with_parent=False, with_child=False):
        obj = cls.model_construct(
            id=odoo_rec.id, name=odoo_rec.name, level=odoo_rec.level
        )
        if with_child and odoo_rec.univers:
            univers_categs = odoo_rec.shopinvader_univers_child_ids
            children = univers_categs.filtered(lambda c: c.level == 0)
            obj.childs = [
                ShortProductCategory.from_product_category_univers(
                    child, univers_categs=univers_categs
                )
                for child in children
            ]
        return obj

    @classmethod
    def from_product_category_univers(cls, odoo_rec, univers_categs=False):
        obj = cls.from_product_category(odoo_rec)
        if univers_categs:
            children = cls._get_children(odoo_rec) & univers_categs
            obj.childs = [
                ShortProductCategory.from_product_category_univers(
                    child, univers_categs=univers_categs
                )
                for child in children
            ]
        return obj

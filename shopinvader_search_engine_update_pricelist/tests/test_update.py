# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopinvader_search_engine.tests.common import TestCategoryBindingBase

from .common import TestMultiProductBindingBase


class TestPriceListItemUpdate(TestMultiProductBindingBase, TestCategoryBindingBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_binding.state = "done"
        cls.product_2_binding.state = "done"

    def test_update_pricelist_item_variant(self):
        self.assertEqual(self.product_binding.state, "done")
        self.pricelist_item.fixed_price = 50
        self.assertEqual(self.product_binding.state, "to_recompute")
        self.assertEqual(self.product_2_binding.state, "done")

    def test_update_pricelist_item_category(self):
        self.assertEqual(self.product_binding.state, "done")
        self.assertEqual(self.product_2_binding.state, "done")
        self.pricelist_item.write(
            {
                "categ_id": self.product.product_tmpl_id.categ_id.id,
                "applied_on": "2_product_category",
            }
        )
        self.assertEqual(self.product_binding.state, "to_recompute")
        self.assertEqual(self.product_2_binding.state, "to_recompute")

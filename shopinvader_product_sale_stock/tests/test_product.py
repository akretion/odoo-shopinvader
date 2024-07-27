# Copyright 2018 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopinvader_product_stock.tests.common import StockCommonCase


class TestProductProduct(StockCommonCase):
    """Tests for product stock info."""

    @classmethod
    def setUpClass(cls):
        super(TestProductProduct, cls).setUpClass()
        cls.shopinvader_product = cls.product.shopinvader_bind_ids
        cls.company = cls.env.ref("base.main_company")
        cls.shopinvader_backend.default_sale_ok_policy = "accept_order"
        cls.company.stock_state_threshold = 0
        cls.shopinvader_product.record_id.sale_ok = False
        cls.shopinvader_product.in_stock_delay = "3 days"
        cls.shopinvader_product.out_of_stock_delay = "10 days"

    def test_out_of_stock_delay(self):
        self.assertEqual(
            self.shopinvader_product.sale_delay,
            "10 days",
        )

    def test_in_stock_delay(self):
        self._add_stock_to_product(self.product, self.loc_1, 20)
        self.assertEqual(
            self.shopinvader_product.sale_delay,
            "3 days",
        )

    def test_sale_ok(self):
        self.assertFalse(self.shopinvader_product.sale_ok)
        self.shopinvader_product.record_id.sale_ok = True
        self.assertTrue(self.shopinvader_product.sale_ok)
        self.shopinvader_product.sale_ok_policy = "refuse_order"
        self.assertFalse(self.shopinvader_product.sale_ok)
        self._add_stock_to_product(self.product, self.loc_1, 20)
        self.assertTrue(self.shopinvader_product.sale_ok)

# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command

from odoo.addons.shopinvader_search_engine.tests.common import (
    TestBindingIndexBase,
    TestProductBindingMixin,
)


class TestMultiProductMixin(TestProductBindingMixin):
    @classmethod
    def setup_records(cls, tst_cls, backend=None):
        res = super().setup_records(tst_cls, backend=backend)
        tst_cls.product_2 = tst_cls.env.ref(
            "shopinvader_product.product_product_chair_vortex_blue"
        )
        tst_cls.product_2_binding = tst_cls.product_2._add_to_index(
            tst_cls.se_product_index
        )

        tst_cls.pricelist_item = tst_cls.env["product.pricelist.item"].create(
            {
                "compute_price": "fixed",
                "product_id": tst_cls.product.id,
                "applied_on": "0_product_variant",
                "fixed_price": 70,
            }
        )
        tst_cls.pricelist = tst_cls.env["product.pricelist"].create(
            {
                "name": "Test pricelist",
                "item_ids": [Command.link(tst_cls.pricelist_item.id)],
            }
        )
        return res


class TestMultiProductBindingBase(TestBindingIndexBase, TestMultiProductMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        TestMultiProductMixin.setup_records(cls)

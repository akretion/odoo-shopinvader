# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

from odoo.addons.extendable.tests.common import ExtendableMixin
from odoo.addons.stock_packaging_calculator.tests.common import TestCommon

from ..schemas import ProductProduct
from .common import CommonPackagingCase


class TestProductPackagingData(CommonPackagingCase, ExtendableMixin, TestCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.init_extendable_registry()
        cls.addClassCleanup(cls.reset_extendable_registry)

    def test_product_packaging_schema(self):
        res = ProductProduct.from_product_product(self.product_a).model_dump()
        packaging = res["packaging"][0]
        self.assertIn("sales", packaging)

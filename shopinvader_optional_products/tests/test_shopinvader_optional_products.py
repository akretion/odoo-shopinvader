# Copyright 2024 Akretion (http://www.akretion.com)
# Olivier Nibart <olivier.nibart@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import SavepointCase

from odoo.addons.shopinvader.tests.common import _install_lang_odoo


class ShopinvaderOptionalProducts(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # time saver
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        lang = _install_lang_odoo(cls.env, "base.lang_fr")
        cls.backend = cls.env.ref("shopinvader.backend_1")
        cls.backend.lang_ids |= lang
        cls.backend.bind_all_product()

    def test_compute_optional_products(self):
        customizable_product_id = self.env.ref(
            "product.product_product_13_product_template"
        )
        optional_product_ids = customizable_product_id.optional_product_ids
        optional_product_ids.optional_product_ids = [(5, 0, 0)]
        optional_variant_ids = optional_product_ids.product_variant_ids
        for (
            shopinvader_variant_id
        ) in customizable_product_id.shopinvader_bind_ids.shopinvader_variant_ids:
            optional_products = shopinvader_variant_id.optional_products
            self.assertEqual(len(optional_products), len(optional_variant_ids))
            shopinvader_options_variant_ids = self.env["shopinvader.variant"].browse(
                [x["id"] for x in optional_products]
            )
            self.assertTrue(
                all(
                    [
                        x.backend_id == shopinvader_variant_id.backend_id
                        for x in shopinvader_options_variant_ids
                    ]
                )
            )
            self.assertTrue(
                all(
                    [
                        x.lang_id == shopinvader_variant_id.lang_id
                        for x in shopinvader_options_variant_ids
                    ]
                )
            )
            for shopinvader_options_variant_id in shopinvader_options_variant_ids:
                self.assertEqual([], shopinvader_options_variant_id.optional_products)

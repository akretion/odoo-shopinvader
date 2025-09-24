# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product_template_multi_link.tests.test_product import (
    ProductLinkCaseBase,
)


class ProductVariantLinkCaseBase(ProductLinkCaseBase):
    @classmethod
    def _create_links(cls):
        cls.template_4 = cls.env.ref("product.product_product_4_product_template")
        cls.template_4.product_template_link_ids.unlink()
        cls.variant_4_1 = cls.env.ref("product.product_product_4")  # steel, white
        cls.variant_4_2 = cls.env.ref("product.product_product_4b")  # steel, black
        cls.variant_4_3 = cls.env.ref("product.product_product_4c")  # aluminium, white
        # Deactivate the other variants to be sure they are not used in the tests
        (
            cls.template_4.product_variant_ids
            - (cls.variant_4_1 | cls.variant_4_2 | cls.variant_4_3)
        ).active = False
        cls.attr_a = cls.env.ref("product.product_attribute_value_2")  # aluminium
        cls.attr_s = cls.env.ref("product.product_attribute_value_1")  # steel
        cls.attr_w = cls.env.ref("product.product_attribute_value_3")  # white
        cls.attr_b = cls.env.ref("product.product_attribute_value_4")  # black
        cls.shopinvader_variant_4_1 = cls.variant_4_1._get_invader_variant(
            cls.backend, "en_US"
        )
        cls.shopinvader_variant_4_2 = cls.variant_4_2._get_invader_variant(
            cls.backend, "en_US"
        )
        cls.shopinvader_variant_4_3 = cls.variant_4_3._get_invader_variant(
            cls.backend, "en_US"
        )
        cls.alias_4_1_3 = cls.env["product.alias"].create(
            {
                "name": "Thelma white",
                "product_tmpl_id": cls.template_4.id,
                "attribute_value_ids": [(6, 0, [cls.attr_w[0].id])],
            }
        )
        cls.alias_4_2 = cls.env["product.alias"].create(
            {
                "name": "Thelma black",
                "product_tmpl_id": cls.template_4.id,
                "attribute_value_ids": [(6, 0, [cls.attr_b[0].id])],
            }
        )

        cls.link_upselling_1_2 = cls.env["product.template.link"].create(
            {
                "left_product_tmpl_id": cls.template_1.id,
                "left_product_id": cls.variant_1_2.id,
                "right_product_tmpl_id": cls.template_2.id,
                "type_id": cls.up_selling_type.id,
            }
        )
        cls.link_crosselling_1_3 = cls.env["product.template.link"].create(
            {
                "left_product_tmpl_id": cls.template_4.id,
                "left_product_alias_id": cls.alias_4_1_3.id,
                "right_product_tmpl_id": cls.template_3.id,
                "right_product_id": cls.variant_3_2.id,
                "type_id": cls.cross_selling_type.id,
            }
        )
        cls.link_crosselling_2_3 = cls.env["product.template.link"].create(
            {
                "left_product_tmpl_id": cls.template_2.id,
                "left_product_id": cls.variant_2_2.id,
                "right_product_tmpl_id": cls.template_3.id,
                "right_product_id": cls.variant_3_2.id,
                "type_id": cls.cross_selling_type.id,
            }
        )
        cls.link_one_way_3_2 = cls.env["product.template.link"].create(
            {
                "left_product_tmpl_id": cls.template_4.id,
                "left_product_alias_id": cls.alias_4_2.id,
                "right_product_tmpl_id": cls.template_3.id,
                "type_id": cls.link_type_asym.id,
            }
        )


class ProductLinkCase(ProductVariantLinkCaseBase):
    def test_product_fallback_links_1_1(self):
        # 1st variant from template 1 gets nothing
        expected = {}
        self.assertEqual(self.shopinvader_variant_1_1.product_links, expected)

    def test_product_fallback_links_1_2(self):
        # 2nd variant gets links w/ template 2 main variant
        main2 = self.template_2.mapped(
            "shopinvader_bind_ids.shopinvader_variant_ids"
        ).filtered(lambda x: x.main)
        expected = {
            "up_selling": [{"id": main2.record_id.id}],
        }
        self.assertEqual(self.shopinvader_variant_1_2.product_links, expected)

    def test_product_fallback_links_2_1(self):
        # and variant from template 2 gets links w/ variant 2 from template 1
        expected = {
            "up_selling": [{"id": self.variant_1_2.id}],
        }
        self.assertEqual(self.shopinvader_variant_2_1.product_links, expected)

    def test_product_fallback_links_2_2(self):
        expected = {
            "up_selling": [{"id": self.variant_1_2.id}],
            "cross_selling": [{"id": self.variant_3_2.id}],
        }
        self.assertEqual(self.shopinvader_variant_2_2.product_links, expected)

    def test_product_alias_links_4_1_3(self):
        # 2nd variant gets links w/ template 1 and 2 variants
        expected = {
            "cross_selling": [
                {"id": self.variant_3_2.id},
            ],
        }
        self.assertEqual(self.shopinvader_variant_4_1.product_links, expected)
        self.assertEqual(self.shopinvader_variant_4_3.product_links, expected)

    def test_product_alias_links_rev_1(self):
        # And the reverse
        expected = {
            "cross_selling": [
                {"id": self.variant_4_1.id},
                {"id": self.variant_2_2.id},
            ],
        }
        self.assertEqual(self.shopinvader_variant_3_2.product_links, expected)

    def test_product_alias_links_asym(self):
        # 1st variant from template 3 gets nothing
        expected = {}
        self.assertEqual(self.shopinvader_variant_3_1.product_links, expected)

    def test_product_alias_links_rev_asym(self):
        # 2nd variant from template 4 gets links w/ template 3 main variant from alias
        main3 = self.template_3.mapped(
            "shopinvader_bind_ids.shopinvader_variant_ids"
        ).filtered(lambda x: x.main)
        expected = {
            "one_way": [{"id": main3.record_id.id}],
        }
        self.assertEqual(self.shopinvader_variant_4_2.product_links, expected)

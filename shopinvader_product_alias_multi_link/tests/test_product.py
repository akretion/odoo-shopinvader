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
        cls.attr_a = cls.env.ref("product.product_attribute_value_2")  # aluminium
        cls.attr_s = cls.env.ref("product.product_attribute_value_1")  # steel
        cls.attr_w = cls.env.ref("product.product_attribute_value_3")  # white
        cls.shopinvader_variant_4_1 = cls.variant_4_1._get_invader_variant(
            cls.backend, "en_US"
        )
        cls.shopinvader_variant_4_2 = cls.variant_4_2._get_invader_variant(
            cls.backend, "en_US"
        )
        cls.shopinvader_variant_4_3 = cls.variant_4_3._get_invader_variant(
            cls.backend, "en_US"
        )
        cls.alias_1 = cls.env["product.alias"].create(
            {
                "name": "Alias for Thelma",
                "product_tmpl_id": cls.template_4.id,
                "attribute_value_ids": [(6, 0, [cls.attr_s[0].id])],
            }
        )

        cls.link_upselling_1_2 = cls.env["product.template.link"].create(
            {
                "left_product_tmpl_id": cls.template_1.id,
                "left_product_id": cls.variant_1_2.id,
                "right_product_tmpl_id": cls.template_2.id,
                "right_product_id": cls.variant_2_2.id,
                "type_id": cls.up_selling_type.id,
            }
        )
        cls.link_crosselling_1_3 = cls.env["product.template.link"].create(
            {
                "left_product_tmpl_id": cls.template_1.id,
                "left_product_id": cls.variant_1_2.id,
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
        cls.link_upselling_1_4a1 = cls.env["product.template.link"].create(
            {
                "left_product_tmpl_id": cls.template_4.id,
                "left_product_id": cls.variant_4_3.id,
                "right_product_tmpl_id": cls.template_4.id,
                "right_product_alias_id": cls.alias_1.id,
                "type_id": cls.up_selling_type.id,
            }
        )
        cls.link_one_way_3_2 = cls.env["product.template.link"].create(
            {
                "left_product_tmpl_id": cls.template_3.id,
                "left_product_id": cls.variant_3_2.id,
                "right_product_tmpl_id": cls.template_2.id,
                "right_product_id": cls.variant_2_2.id,
                "type_id": cls.link_type_asym.id,
            }
        )


class ProductLinkCase(ProductVariantLinkCaseBase):
    # Check that everything still works without using aliases and empty variants

    def test_links(self):
        # the result is the same for each product and it matches the main variant only
        main1 = self.template_1.mapped(
            "shopinvader_bind_ids.shopinvader_variant_ids"
        ).filtered(lambda x: x.main)
        main2 = self.template_2.mapped(
            "shopinvader_bind_ids.shopinvader_variant_ids"
        ).filtered(lambda x: x.main)
        main3 = self.template_3.mapped(
            "shopinvader_bind_ids.shopinvader_variant_ids"
        ).filtered(lambda x: x.main)

        expected = {
            "up_selling": [{"id": main2.record_id.id}],
            "cross_selling": [{"id": main3.record_id.id}],
        }
        self.assertEqual(
            self.shopinvader_variant_1_1.shopinvader_product_id.product_links,
            expected,
        )
        self.assertEqual(
            self.shopinvader_variant_1_2.shopinvader_product_id.product_links,
            expected,
        )

        expected = {
            "cross_selling": [{"id": main3.record_id.id}],
            "up_selling": [{"id": main1.record_id.id}],
        }
        self.assertEqual(
            self.shopinvader_variant_2_1.shopinvader_product_id.product_links,
            expected,
        )
        self.assertEqual(
            self.shopinvader_variant_2_2.shopinvader_product_id.product_links,
            expected,
        )
        expected = {
            "cross_selling": [
                {"id": main1.record_id.id},
                {"id": main2.record_id.id},
            ],
        }
        expected["one_way"] = [{"id": main2.record_id.id}]
        self.assertEqual(
            self.shopinvader_variant_3_2.shopinvader_product_id.product_links,
            expected,
        )

    def test_link_json_data(self):
        exporter = self.env.ref("shopinvader.ir_exp_shopinvader_variant")
        parser = exporter.get_json_parser()
        self.assertIn("links", self.shopinvader_variant_2_2.jsonify(parser, one=True))

    def test_links_tmpl1(self):
        # 1st variant from template 1 gets nothing
        expected = {}
        self.assertEqual(self.shopinvader_variant_1_1.product_links, expected)
        # 2nd variant gets links w/ template 2 and 3 variants
        expected = {
            "up_selling": [{"id": self.variant_2_2.id}],
            "cross_selling": [{"id": self.variant_3_2.id}],
        }
        self.assertEqual(self.shopinvader_variant_1_2.product_links, expected)

    def test_links_tmpl2(self):
        # 1st variant from template 2 gets nothing
        expected = {}
        self.assertEqual(self.shopinvader_variant_2_1.product_links, expected)
        # 2nd variant gets links w/ template 2 and 3 variants
        expected = {
            "up_selling": [{"id": self.variant_1_2.id}],
            "cross_selling": [{"id": self.variant_3_2.id}],
        }
        self.assertEqual(self.shopinvader_variant_2_2.product_links, expected)

    def test_links_tmpl3(self):
        # 1st variant from template 3 gets nothing
        expected = {}
        self.assertEqual(self.shopinvader_variant_3_1.product_links, expected)
        # 2nd variant gets links w/ template 1 and 2 variants
        expected = {
            "cross_selling": [
                {"id": self.variant_1_2.id},
                {"id": self.variant_2_2.id},
            ],
            "one_way": [{"id": self.variant_2_2.id}],
        }
        self.assertEqual(self.shopinvader_variant_3_2.product_links, expected)

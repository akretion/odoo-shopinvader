# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ShopinvaderVariant(models.Model):
    _inherit = "shopinvader.variant"

    def _get_product_links(self):
        # Consider all links where the product is involved,
        # non matching (alias / variant filtered) will be removed when looking
        # for the target
        return self.product_template_link_ids

    def _product_link_target(self, link):
        # Determine the target product (variant, alias or template) depending
        # on the specificity of the link for both sides
        right_target = (
            link.right_product_id
            or link.right_product_alias_id
            or link.right_product_tmpl_id
        )
        left_target = (
            link.left_product_id
            or link.left_product_alias_id
            or link.left_product_tmpl_id
        )

        # Check from most specific to least specific
        # Variant match
        if link.left_product_id == self.record_id:
            return right_target
        if link.type_id.is_symmetric and link.right_product_id == self.record_id:
            return left_target

        # Alias match
        if self.alias_id:
            if not link.left_product_id and link.left_product_alias_id == self.alias_id:
                return right_target
            if (
                not link.right_product_id
                and link.type_id.is_symmetric
                and link.right_product_alias_id == self.alias_id
            ):
                return left_target

        # Template match
        if (
            not link.left_product_id
            and not link.left_product_alias_id
            and link.left_product_tmpl_id == self.record_id.product_tmpl_id
        ):
            return right_target
        if (
            not link.right_product_id
            and not link.right_product_alias_id
            and link.type_id.is_symmetric
            and link.right_product_tmpl_id == self.record_id.product_tmpl_id
        ):
            return left_target

    def _product_link_target_variant(self, target):
        if target._name == "product.product":
            return super()._product_link_target_variant(target)

        alias = None
        if target._name == "product.alias":
            # Get the template from the alias
            alias = target
            target = target.product_tmpl_id

        # Reuse shopinvader.product logic but handle aliases if needed
        for shopinvader_variant in target.shopinvader_bind_ids.shopinvader_variant_ids:
            # Get bindings of the correct backend and lang, pick only
            # the main one or the one matching the alias
            if (
                shopinvader_variant.backend_id == self.backend_id
                and shopinvader_variant.lang_id == self.lang_id
                and (
                    shopinvader_variant.main
                    if alias is None
                    else shopinvader_variant.alias_id == alias
                )
            ):
                return shopinvader_variant

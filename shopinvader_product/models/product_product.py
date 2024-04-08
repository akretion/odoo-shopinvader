# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from itertools import groupby

from odoo import api, fields, models

from odoo.addons.base_sparse_field.models.fields import Serialized

from .tools import sanitize_attr_name


class ProductProduct(models.Model):
    _inherit = "product.product"

    variant_attributes = Serialized(
        compute="_compute_variant_attributes", string="Shopinvader Attributes"
    )
    attribute_value_ids = fields.Many2many(
        comodel_name="product.attribute.value",
        compute="_compute_attribute_value_ids",
        readonly=True,
    )
    short_name = fields.Char(compute="_compute_names")
    full_name = fields.Char(compute="_compute_names")
    main = fields.Boolean(compute="_compute_main_product")

    def _compute_variant_attributes(self):
        for record in self:
            variant_attributes = dict()
            for att_value in record.attribute_value_ids:
                sanitized_key = sanitize_attr_name(att_value.attribute_id)
                variant_attributes[sanitized_key] = att_value.name
            record.variant_attributes = variant_attributes

    @api.depends("product_template_attribute_value_ids")
    def _compute_attribute_value_ids(self):
        for record in self:
            record.attribute_value_ids = record.mapped(
                "product_template_attribute_value_ids.product_attribute_value_id"
            )

    def _prepare_variant_name_and_short_name(self):
        self.ensure_one()
        attributes = self.attribute_value_ids
        short_name = ", ".join(attributes.mapped("name"))
        full_name = self.display_name
        if short_name:
            full_name += " (%s)" % short_name
        return full_name, short_name

    def _compute_names(self):
        for record in self:
            (
                record.full_name,
                record.short_name,
            ) = record._prepare_variant_name_and_short_name()

    @api.model
    def _get_shopinvader_product_variants(self, product_ids):
        # Use sudo to bypass permissions (we don't care)
        return self.sudo().search(
            [("product_tmpl_id", "in", product_ids)], order="product_tmpl_id"
        )

    @api.model
    def _get_main_product_read_fields(self):
        product_model = self.env["product.product"]
        order_by = [x.strip() for x in product_model._order.split(",")]
        return ["product_tmpl_id"] + [f.split(" ")[0] for f in order_by]

    @api.model
    def _get_main_product_sorted_variants(self, variants):
        order_by = [x.strip() for x in self.env["product.product"]._order.split(",")]

        def get_value(record, key):
            if record[key] is False and self._fields[key].type in ("char", "text"):
                return ""
            else:
                return record[key]

        for order_key in reversed(order_by):
            order_key_split = order_key.split(" ")
            reverse = len(order_key_split) > 1 and order_key_split[1] == "desc"
            variants.sort(
                key=lambda var: get_value(var, order_key_split[0]),
                reverse=reverse,
            )

        return variants

    @api.model
    def _pick_main_variant(self, variants):
        ordered = self._get_main_product_sorted_variants(variants)
        return ordered[0].get("id") if ordered else None

    def _compute_main_product(self):
        # Respect same order.
        fields_to_read = self._get_main_product_read_fields()
        product_ids = self.mapped("product_tmpl_id").ids
        _variants = self._get_shopinvader_product_variants(product_ids)
        # Use `load=False` to not load template name
        variants = _variants.read(fields_to_read, load=False)
        var_by_product = groupby(variants, lambda x: x["product_tmpl_id"])

        main_by_product = {
            product: self._pick_main_variant(list(variants))
            for product, variants in var_by_product
        }
        for record in self:
            record.main = main_by_product.get(record.product_tmpl_id.id) == record.id

# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo.addons.component.core import Component


def to_date(value):
    return date.fromisoformat(value)


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    def _convert_one_line(self, line):
        res = super()._convert_one_line(line)
        res.update({"gift_card_id": line.gift_card_ids.id})
        return res

    def _add_item(self, cart, params):
        self._check_allowed_product(cart, params)
        item = None
        product = self.env["product.product"].browse(params["product_id"])
        gift_tmpl = product.product_tmpl_id.gift_cart_template_ids
        if gift_tmpl:
            # When the product is a gift card, always create a new line, never edit it
            with self.env.norecompute():
                item = self._create_cart_line(cart, params)
            item.price_unit = params.get("initial_amount")
            self._create_gift_cards(item, gift_tmpl, params)
            cart.recompute()
        else:
            item = super()._add_item(cart, params)
        return item

    def _create_gift_cards(self, item, gift_card_tmpl, params):
        card = self.env["gift.card"].search(
            [
                ("sale_line_id", "=", item.id),
            ]
        )
        if not card:
            vals = {
                "sale_line_id": item.id,
                "initial_amount": params.get("initial_amount"),
                "is_divisible": gift_card_tmpl.is_divisible,
                "duration": gift_card_tmpl.duration,
                "gift_card_tmpl_id": gift_card_tmpl.id,
                "comment": params.get("comment"),
                "beneficiary_name": params.get("beneficiary_name"),
                "beneficiary_email": params.get("beneficiary_email"),
                "buyer_id": params.get("buyer_id"),
                "buyer_name": params.get("buyer_name"),
                "buyer_email": params.get("buyer_email"),
                "shopinvader_backend_id": self.shopinvader_backend.id,
            }
            if "start_date" in params and params.get("start_date"):
                vals["start_date"] = params.get("start_date")
            card = self.env["gift.card"].create(vals)
        return card

    def _get_gift_card_schema(self):
        return {
            "initial_amount": {"coerce": float, "required": False, "type": "float"},
            "start_date": {"type": "date", "coerce": to_date},
            "comment": {"type": "string", "required": False},
            "beneficiary_name": {"type": "string", "required": False},
            "beneficiary_email": {"type": "string", "required": False},
            "buyer_id": {
                "coerce": int,
                "required": False,
                "type": "integer",
            },
            "buyer_name": {"type": "string", "required": False},
            "buyer_email": {"type": "string", "required": False},
        }

    def _validator_add_item(self):
        res = super()._validator_add_item()
        res.update(self._get_gift_card_schema())
        return res

    def _validator_update_item(self):
        res = super()._validator_update_item()
        res.update(self._get_gift_card_schema())
        return res

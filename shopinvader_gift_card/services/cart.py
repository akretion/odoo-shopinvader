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
        res.update({"gift_card_ids": line.gift_card_ids.ids})
        return res

    def _add_item(self, cart, params):
        item = super()._add_item(cart, params)
        gift_tmpl = item.product_id.product_tmpl_id.gift_cart_template_ids
        if gift_tmpl:
            item.price_unit = params.get("initial_amount")
            cards = self._create_gift_cards(item, gift_tmpl, params)
            item.gift_card_ids = cards
        return item

    def _create_gift_cards(self, item, gift_card_tmpl, params):
        cards = self.env["gift.card"].search(
            [
                ("sale_line_id", "=", item.id),
            ]
        )
        while len(cards) < int(item.product_uom_qty):
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
            new_card = self.env["gift.card"].create(vals)
            cards |= new_card
        return cards

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

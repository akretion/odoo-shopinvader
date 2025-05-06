# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    def _prepare_transfer_cart_line(self, line):
        res = super()._prepare_transfer_cart_line(line)
        res["skip_coupon_recompute"] = True
        return res

    def _get_transfer_order_lines(self, cart):
        return cart._get_paid_order_lines()

    def _merge_cart(self, anonymous_cart, partner_cart):
        super()._merge_cart(anonymous_cart, partner_cart)

        # First add sale_coupon_deferred_coupon_dedup unconfirmed_coupon_ids
        # This part should be in a glue module
        unconfirmed_coupon_ids = anonymous_cart.unconfirmed_applied_coupon_ids.filtered(
            lambda c: c.state not in ["used", "expired", "cancel"]
        ).ids
        anonymous_cart.write({"unconfirmed_applied_coupon_ids": [(5, 0, 0)]})
        partner_cart.write(
            {
                "unconfirmed_applied_coupon_ids": [
                    (4, coupon_id) for coupon_id in unconfirmed_coupon_ids
                ]
            }
        )

        # Then add sale_coupon applied_coupon_ids
        coupon_ids = anonymous_cart.applied_coupon_ids.filtered(
            lambda c: c.state not in ["used", "expired", "cancel"]
        ).ids
        anonymous_cart.write({"applied_coupon_ids": [(5, 0, 0)]})
        partner_cart.write(
            {"applied_coupon_ids": [(4, coupon_id) for coupon_id in coupon_ids]}
        )
        partner_cart.recompute_coupon_lines()

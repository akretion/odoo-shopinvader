import logging

from odoo import _, fields
from odoo.exceptions import AccessDenied

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    def _decode_token(self, token):
        validator = self.env["auth.jwt.validator"]._get_validator_by_name(
            validator_name="shopinvader"
        )
        while validator:
            try:
                return validator._decode(token)
            except Exception:
                validator = validator.next_validator_id

    def _validator_transfer(self):
        return {
            "token": {"type": "string", "required": True},
        }

    def transfer(self, token=None):
        cart = self._get()
        auth_token = self._decode_token(token)
        if not auth_token or not auth_token.get("email"):
            raise AccessDenied(_("Invalid new auth token"))

        partner = self.env["shopinvader.partner"].search(
            [
                ("partner_email", "=", auth_token["email"]),
                ("backend_id", "=", self.shopinvader_backend.id),
            ]
        )

        if len(partner) != 1:
            raise AccessDenied(_("Invalid partner email in token"))

        old_cart = None
        if self.shopinvader_backend.merge_cart_on_transfer:
            old_partner = self.work.partner
            self.work.partner = partner.record_id
            old_cart = self._get(False)
            self.work.partner = old_partner

        # Change cart partner:
        res_partner_id = partner.record_id.id
        cart.date_order = fields.Datetime.now()
        cart.write_with_onchange(
            {
                "partner_id": res_partner_id,
                "partner_shipping_id": res_partner_id,
                "partner_invoice_id": res_partner_id,
            }
        )

        if old_cart and self.shopinvader_backend.merge_cart_on_transfer:
            # Merge cart:
            for line in old_cart.order_line:
                try:
                    self._add_item(
                        cart,
                        {
                            "product_id": line.product_id.id,
                            "item_qty": line.product_uom_qty,
                            # shopinvader_sale_coupon compat:
                            # Prevent incremental recomputation
                            "skip_coupon_recompute": True,
                        },
                    )
                except Exception:
                    _logger.warning(
                        "Error while adding item %s to cart",
                        line.product_id,
                        exc_info=True,
                    )
            # Sale coupon compat (should be in a separate module but hey...)
            if hasattr(self, "recompute_coupon_lines"):
                self.recompute_coupon_lines(cart)

        return self._to_json(cart)

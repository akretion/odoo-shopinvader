import logging

from odoo import _
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
        anonymous_cart = self._get()
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

        # Swap partner to non anonymous partner
        self.work.invader_partner = partner
        self.work.invader_partner_user = partner
        self.work.partner = partner.record_id
        self.work.partner_user = partner.record_id

        if self.shopinvader_backend.merge_cart_on_transfer:
            partner_cart = self._get()
        else:
            partner_cart = self._create_empty_cart()

        self._merge_cart(anonymous_cart, partner_cart)
        return self._to_json(partner_cart)

    def _prepare_transfer_cart_line(self, line):
        return {
            "product_id": line.product_id.id,
            "item_qty": line.product_uom_qty,
        }

    def _get_transfer_order_lines(self, cart):
        return cart.order_line

    def _merge_cart(self, anonymous_cart, partner_cart):
        # Merge cart:
        for line in self._get_transfer_order_lines(anonymous_cart):
            try:
                self._add_item(partner_cart, self._prepare_transfer_cart_line(line))
            except Exception:
                _logger.warning(
                    "Error while adding item %s to cart",
                    line.product_id,
                    exc_info=True,
                )

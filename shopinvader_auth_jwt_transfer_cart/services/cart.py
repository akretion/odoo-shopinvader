from odoo import _, fields
from odoo.exceptions import AccessDenied, UserError

from odoo.addons.component.core import Component


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
            [("partner_email", "=", auth_token["email"])]
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

        if (
            old_cart
            and old_cart.order_line
            and self.shopinvader_backend.merge_cart_on_transfer
        ):
            self._merge_cart(old_cart, cart)

        return self._to_json(cart)

    def _merge_cart(self, old_cart, cart):
        # Merge cart:
        for line in old_cart.order_line:
            self._merge_cart_line(cart, line)

        cart.recompute()

        # Trigger normal add_item hooks once with an empty add hack:
        # Avoid to trigger the hook for each line
        # Also avoid creating explicit glue modules for shopinvader_sale_coupon,
        # shopinvader_delivery_carrier, shopinvader_gift_card, etc.
        if cart.order_line:
            self._add_item(
                cart, {"product_id": cart.order_line[0].product_id.id, "item_qty": 0}
            )

    def _merge_cart_line(self, cart, line):
        params = {
            "product_id": line.product_id.id,
            "item_qty": line.product_uom_qty,
        }

        # Don't raise error if product is not available, just ignore
        try:
            self._check_allowed_product(cart, params)
        except UserError:
            return

        item = self._check_existing_cart_item(cart, params)
        if item:
            self._upgrade_cart_item_quantity(cart, item, params, action="sum")
        else:
            with self.env.norecompute():
                item = self._create_cart_line(cart, params)

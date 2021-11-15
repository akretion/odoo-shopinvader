from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    def _remove_coupon(self, cart, params):
        super()._remove_coupon(cart, params)
        self._recompute_coupon_lines(cart, params)

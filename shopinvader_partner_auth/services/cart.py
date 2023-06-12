# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    # Change _get cart behaviour as cart id do not exist anymore
    # with partner_auth and V2 cart
    def _get(self, create_if_not_found=True):
        cart = super()._get(create_if_not_found=False)
        if not cart and self.partner:
            domain = [
                ("shopinvader_backend_id", "=", self.shopinvader_backend.id),
                ("typology", "=", "cart"),
                ("state", "=", "draft"),
                ("partner_id", "=", self.partner.id),
            ]
            cart = self.env["sale.order"].search(domain)
        if not cart and create_if_not_found:
            cart = self._create_empty_cart()
        return cart

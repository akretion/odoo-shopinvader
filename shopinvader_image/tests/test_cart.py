# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_v1_base.tests.test_cart import CommonConnectedCartCase


class ShopinvaderCartCase(CommonConnectedCartCase):
    def test_get_cart_image_info(self):
        self.backend.bind_all_product()
        response = self.service.dispatch("search")
        self.assertIn("images", response["data"]["lines"]["items"][0]["product"])

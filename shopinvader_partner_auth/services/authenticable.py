# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class PortalAuthenticable(Component):
    _inherit = ["base.authenticable", "base.shopinvader.service"]
    _name = "shopinvader.authenticable"

    def _get_directory(self):
        return self.shopinvader_backend.sudo().directory_auth_id

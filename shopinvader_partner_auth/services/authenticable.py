# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class PortalAuthenticable(Component):
    _inherit = ["base.authenticable", "base.shopinvader.service"]
    _name = "shopinvader.authenticable"

    def _get_directory(self):
        return self.shopinvader_backend.sudo().directory_auth_id

    def _create_partner_auth(self, params):
        partner_auth = super()._create_partner_auth(params)
        # Create shopinvader binding as it's mandatory for V14
        # Do not export it to locomotive as it's not needed
        self.env["shopinvader.partner"].sudo().with_context(
            no_connector_export=True
        ).create(
            {
                "record_id": partner_auth.partner_id.id,
                "backend_id": self.shopinvader_backend.id,
            }
        )
        return partner_auth

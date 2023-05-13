# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.http import request

from odoo.addons.component.core import Component


class ShopinvaderPartnerAuthServiceContextProvider(Component):
    _name = "partner_auth.shopinvader.service.context.provider"
    _inherit = "shopinvader.service.context.provider"
    _usage = "shopinvader_partner_auth_component_context_provider"

    def _get_shopinvader_partner(self):
        partner_id = self._get_authenticated_partner_id()
        backend = self._get_backend()
        if partner_id:
            partner = self.env["res.partner"].browse(partner_id)
            return partner.shopinvader_bind_ids.filtered(
                lambda s: s.backend_id == backend
            )
        else:
            return self.env["shopinvader.partner"]

    def _get_authenticated_partner_id(self):
        if hasattr(request, "auth_res_partner_id"):
            return request.auth_res_partner_id


class ShopinvaderPartnerAuthV2ServiceContextProvider(Component):
    _name = "partner_auth.shopinvader.v2.service.context.provider"
    _inherit = "partner_auth.shopinvader.service.context.provider"
    _collection = "shopinvader.api.v2"

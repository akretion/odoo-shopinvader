# Copyright 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.http import request

from odoo.addons.base_rest.controllers import main
from odoo.addons.partner_auth.models.directory_auth import COOKIE_AUTH_NAME


class ShopinvaderPartnerAuthController(main.RestController):
    _root_path = "/shopinvader_partner_auth/"
    _collection_name = "shopinvader.backend"
    _default_auth = "partner_auth"
    _default_save_session = False
    _component_context_provider = "shopinvader_partner_auth_component_context_provider"

    def make_response(self, data):
        response = super().make_response(data)
        # add sliding cookies
        if (
            request.httprequest.path.startswith(self._root_path)
            and "sign_out" not in request.httprequest.path
            and hasattr(request, "auth_directory_id")
            and hasattr(request, "auth_res_partner_id")
        ):
            directory = request.env["directory.auth"].browse(request.auth_directory_id)
            cookie_params = directory._prepare_cookie(request.auth_res_partner_id)
            response.set_cookie(COOKIE_AUTH_NAME, **cookie_params)
        return response


class ShopinvaderPartnerAuthV2Controller(ShopinvaderPartnerAuthController):
    _root_path = "/shopinvader_partner_auth/v2/"
    _collection_name = "shopinvader.api.v2"
    _component_context_provider = "shopinvader_partner_auth_component_context_provider"

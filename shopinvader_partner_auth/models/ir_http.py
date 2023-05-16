# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _get_shopinvader_backend(cls):
        """Get the requested shopinvader backend instance"""
        website_unique_key = request.httprequest.environ.get("HTTP_WEBSITE_UNIQUE_KEY")
        return (
            request.env["shopinvader.backend"]
            .sudo()
            ._get_from_website_unique_key(website_unique_key)
        )

    @classmethod
    def _get_directory_auth(cls):
        if request.httprequest.path.startswith("/shopinvader_partner_auth/"):
            return cls._get_shopinvader_backend().directory_auth_id
        else:
            return super()._get_directory_auth()

    @classmethod
    def _prepare_guest_partner(cls):
        return {
            "name": "guest",
            "guest": True,
            "active": False,
        }

    @classmethod
    def _create_guest_partner(cls):
        if hasattr(request, "auth_res_partner_id") and request.auth_res_partner_id:
            return
        # Create guest partner for cart if partner is not logged
        partner = request.env["res.partner"].create(cls._prepare_guest_partner())
        request.auth_res_partner_id = partner.id
        request.auth_directory_id = cls._get_directory_auth().id

    @classmethod
    def _auth_method_public_or_partner_auth(cls):
        super()._auth_method_public_or_partner_auth()
        if request.httprequest.path.startswith(
            "/shopinvader_partner_auth/v2/cart/sync"
        ):
            cls._create_guest_partner()

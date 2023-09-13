from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.api import Environment
from odoo.exceptions import ValidationError

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner_impl,
    fastapi_endpoint_id,
    odoo_env,
)

from ..routers import helpdesk_router


# TODO: Refactor this in a shopinvader_fastapi module
class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"

    shopinvader_backend_id = fields.Many2one(
        comodel_name="shopinvader.backend",
        string="Shopinvader backend",
        ondelete="cascade",
    )
    app: str = fields.Selection(
        selection_add=[("shopinvader_api_helpdesk", "Shopinvader api helpdesk")],
        ondelete={"shopinvader_api_helpdesk": "cascade"},
    )
    shopinvader_api_helpdesk_auth_method = fields.Selection(
        selection=[("api_key", "Api Key")],
        string="Authentication method",
    )

    @api.constrains("app", "demo_auth_method")
    def _valdiate_demo_auth_method(self):
        for rec in self:
            if (
                rec.app == "shopinvader_api_helpdesk"
                and not rec.shopinvader_api_helpdesk_auth_method
            ):
                raise ValidationError(
                    _(
                        "The authentication method is required for app %(app)s",
                        app=rec.app,
                    )
                )

    def _get_fastapi_routers(self) -> List[APIRouter]:
        if self.app == "shopinvader_api_helpdesk":
            return [helpdesk_router]
        return super()._get_fastapi_routers()

    @api.model
    def _fastapi_app_fields(self) -> List[str]:
        fields = super()._fastapi_app_fields()
        fields.append("shopinvader_api_helpdesk_auth_method")
        return fields

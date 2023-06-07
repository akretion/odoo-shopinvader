# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from fastapi import APIRouter

from odoo import api, fields, models


class FastapiEndpoint(models.Model):

    _inherit = "fastapi.endpoint"

    app: str = fields.Selection(
        selection_add=[("invoice", "Invoice Endpoint")], ondelete={"invoice": "cascade"}
    )

    @api.model
    def _get_fastapi_routers(self):
        if self.app == "invoice":
            return [invoice_api_router]
        return super().get_fastapi_routers()


# create a router
invoice_api_router = APIRouter()

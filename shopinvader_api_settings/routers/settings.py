# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import Annotated

from fastapi import APIRouter, Depends

from odoo import api, fields, models

from odoo.addons.fastapi.dependencies import fastapi_endpoint, odoo_env
from odoo.addons.fastapi.models import FastapiEndpoint

from ..schemas import Settings
from ..schemas.country import Country
from ..schemas.partner_title import PartnerTitle

settings_router = APIRouter(tags=["settings"])


@settings_router.get("/settings", response_model=Settings)
def get_settings(
    env: Annotated[api.Environment, Depends(odoo_env)],
    endpoint: Annotated[FastapiEndpoint, Depends(fastapi_endpoint)],
) -> Settings:
    """
    Returns common settings
    """
    return (
        env["shopinvader_api_settings.routers.helper"]
        .new(
            {
                "fastapi_endpoint": endpoint,
            }
        )
        ._get_settings()
    )


class ShopinvaderApiSettingsRouterHelper(models.AbstractModel):
    _name = "shopinvader_api_settings.routers.helper"
    _description = "Shopinvader API Settings Router Helper"

    fastapi_endpoint = fields.Many2one(comodel_name="fastapi.endpoint")

    def _get_settings(self) -> Settings:
        settings = Settings.model_construct(
            countries=self._get_countries(),
            partner_titles=self._get_partner_titles(),
        )
        return settings

    def _get_countries(self) -> list[Country]:
        return [
            Country.from_res_country(country)
            for country in self.env["res.country"].search(self._get_countries_domain())
        ]

    def _get_countries_domain(
        self,
    ) -> list:
        return []

    def _get_partner_titles(self) -> list[PartnerTitle]:
        return [
            PartnerTitle.from_res_partner_title(title)
            for title in self.env["res.partner.title"].search(
                self._get_partner_title_domain()
            )
        ]

    def _get_partner_title_domain(self) -> list:
        return []

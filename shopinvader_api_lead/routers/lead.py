# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated

from fastapi import APIRouter, Depends

from odoo import api

from odoo.addons.fastapi.dependencies import odoo_env

from ..schemas import Lead, LeadInput

lead_router = APIRouter(tags=["leads"])


@lead_router.post("/leads", status_code=201)
def create(
    data: LeadInput,
    env: Annotated[api.Environment, Depends(odoo_env)],
) -> Lead | None:
    lead = env["crm.lead"].create(data.to_crm_lead_vals())
    return Lead.from_crm_lead(lead)

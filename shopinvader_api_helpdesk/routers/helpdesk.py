from typing import Annotated, List

from fastapi import APIRouter, Depends

from odoo import _, api, models
from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)
from ..schemas import HelpdeskTicketInfo, HelpdeskTicketRequest

helpdesk_router = APIRouter(tags=["helpdesk"])


@helpdesk_router.get("/helpdesk_ticket")
@helpdesk_router.get("/helpdesk_ticket/{id}")
def get(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated["ResPartner", Depends(authenticated_partner)],
    id: int | None = None,
) -> List[HelpdeskTicketInfo] | HelpdeskTicketInfo:
    """
    Get tickets
    """
    if id:
        ticket = env["helpdesk.ticket"].browse(id)
        return HelpdeskTicketInfo.from_ticket(ticket) if ticket else None

    tickets = env["helpdesk.ticket"].search([])
    return [HelpdeskTicketInfo.from_ticket(rec) for rec in tickets]


@helpdesk_router.post("/helpdesk_ticket/create", status_code=201)
def create(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    data: HelpdeskTicketRequest,
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> HelpdeskTicketInfo:
    """
    Create ticket for authenticated user
    """
    vals = env["helpdesk.ticket"]._prepare_params_from_fastapi(
        data.dict(), mode="create"
    )
    record = env["helpdesk.ticket"].create(vals)
    if "partner_id" in vals:
        vals.update(
            record.play_onchanges(
                vals,
                [
                    "partner_id",
                ],
            )
        )
        record.write(vals)
    return HelpdeskTicketInfo.from_ticket(record)

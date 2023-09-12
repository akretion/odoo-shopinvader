from typing import Annotated, List

from fastapi import APIRouter, Depends

from odoo import _, api, models
from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)
from ..schemas import HelpdeskTicketInfo

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

from typing import Annotated, List

from fastapi import APIRouter, Depends

from odoo import _, api, models
from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)
from odoo import SUPERUSER_ID
from odoo.api import Environment
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from odoo.addons.fastapi.dependencies import fastapi_endpoint_id, odoo_env
from odoo.addons.shopinvader.models.shopinvader_backend import (
    ShopinvaderBackend,
)
from ..schemas import HelpdeskTicketInfo, HelpdeskTicketRequest

helpdesk_router = APIRouter(tags=["helpdesk"])


# TODO Refactor this in a shopinvader_fastapi(_auth?) module
async def api_key_backend_impl(
    api_key: str = Depends(
        APIKeyHeader(
            name="api-key",
            description="The api key in the header.",
        )
    ),
    _id: int = Depends(fastapi_endpoint_id),
    env: Environment = Depends(odoo_env),
) -> ShopinvaderBackend:
    key = env["auth.api.key"].with_user(SUPERUSER_ID)._retrieve_api_key(api_key)
    endpoint = env["fastapi.endpoint"].sudo().browse(_id)

    if not key or endpoint.shopinvader_backend_id.auth_api_key_id.key != key.key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect API Key"
        )

    return endpoint.shopinvader_backend_id


@helpdesk_router.get("/helpdesk_ticket")
@helpdesk_router.get("/helpdesk_ticket/{id}")
def get(
    env: Annotated[api.Environment, Depends(odoo_env)],
    partner: Annotated["ResPartner", Depends(authenticated_partner)],
    backend: Annotated[ShopinvaderBackend, Depends(api_key_backend_impl)],
    id: int | None = None,
) -> List[HelpdeskTicketInfo] | HelpdeskTicketInfo:
    """
    Get tickets
    """
    breakpoint()
    if id:
        ticket = env["helpdesk.ticket"].browse(id)
        if ticket.shopinvader_backend_id != backend:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
            )
        return HelpdeskTicketInfo.from_ticket(ticket) if ticket else None

    tickets = env["helpdesk.ticket"].search(["shopinvader_backend_id", "=", backend.id])
    return [HelpdeskTicketInfo.from_ticket(rec) for rec in tickets]


@helpdesk_router.post("/helpdesk_ticket/create", status_code=201)
def create(
    env: Annotated[api.Environment, Depends(odoo_env)],
    data: HelpdeskTicketRequest,
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    backend: Annotated[ShopinvaderBackend, Depends(api_key_backend_impl)],
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

# Copyright 2026 Akretion (http://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from odoo import Command, api, fields
from odoo.exceptions import MissingError

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.extendable_fastapi.schemas import PagedCollection
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
    odoo_env,
    paging,
)
from odoo.addons.fastapi.schemas import Paging
from odoo.addons.shopinvader_router_helper import VirtualModel
from odoo.addons.shopinvader_schema_helpdesk.schemas import HelpdeskTicket, HelpdeskTicketSearch, HelpdeskTicketWithDetail

helpdesk_router = APIRouter(tags=["helpdesk"])


class HelpdeskTicketHelper(VirtualModel):
    _inherit = "shopinvader.router.helper"
    _name = "shopinvader_api_helpdesk.helpdesk_router.helper"
    _description = "Shopinvader Api Helpdesk Service Helper"

    _model = "helpdesk.ticket"

    partner = fields.Many2one("res.partner", required=True)

    def _domain(self):
        res = [
            ("partner_id", "=", self.partner.id),
        ]
        return res

    def _prepare_create_values(self, values):
        values = dict(values)
        sale_order_id = values.pop("sale_order_id", None)
        team_id = values.pop("team_id", None)
        values["partner_id"] = self.partner.id
        if sale_order_id:
            # same visibility rule as the /sales endpoint: only the
            # authenticated partner's own sale orders can be linked
            sale_order = self.env["sale.order"].search(
                [("id", "=", sale_order_id), ("partner_id", "=", self.partner.id)]
            )
            if not sale_order:
                raise MissingError(
                    self.env._("Sale order {sale_order_id} not found").format(
                        sale_order_id=sale_order_id
                    )
                )
            values["sale_order_ids"] = [Command.set(sale_order.ids)]
        if team_id:
            # teams are an internal concept, not scoped to a partner: only
            # check that the team exists
            team = self.env["helpdesk.ticket.team"].sudo().search(
                [("id", "=", team_id)]
            )
            if not team:
                raise MissingError(
                    self.env._("Team {team_id} not found").format(team_id=team_id)
                )
            values["team_id"] = team.id
        return values

def helpdesk_helper(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
):
    return env["shopinvader_api_helpdesk.helpdesk_router.helper"].new(
        {"partner": partner}
    )


@helpdesk_router.get("/tickets")
def search(
    params: Annotated[HelpdeskTicketSearch, Depends()],
    helper: Annotated[HelpdeskTicketHelper, Depends(helpdesk_helper)],
    paging: Annotated[Paging, Depends(paging)],
) -> PagedCollection[HelpdeskTicket]:
    """Get the list of current partner's tickets"""
    count, tickets = helper.search_with_count(
        params.to_odoo_domain(helper.env),
        limit=paging.limit,
        offset=paging.offset,
    )
    return PagedCollection[HelpdeskTicket](
        count=count,
        items=[HelpdeskTicket.from_helpdesk_ticket(ticket) for ticket in tickets],
    )


@helpdesk_router.post("/tickets", status_code=201)
def create(
    data: HelpdeskTicket,
    helper: Annotated[HelpdeskTicketHelper, Depends(helpdesk_helper)],
) -> HelpdeskTicketWithDetail:
    """
    Create a new helpdesk ticket for the authenticated partner.

    If sale_order_id is provided and belongs to the authenticated partner,
    the ticket is linked to it.
    """
    ticket = helper.create(data.to_helpdesk_ticket_vals())
    return HelpdeskTicketWithDetail.from_helpdesk_ticket(ticket)


@helpdesk_router.get("/ticket/id/{ticket_id}")
def get_by_id(
    ticket_id: int,
    helper: Annotated[HelpdeskTicketHelper, Depends(helpdesk_helper)],
) -> HelpdeskTicketWithDetail:
    """
    Get the helpdesk ticket from its id
    """
    ticket = helper.get(ticket_id)
    return HelpdeskTicketWithDetail.from_helpdesk_ticket(ticket)

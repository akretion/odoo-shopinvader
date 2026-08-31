# Copyright 2026 Akretion (https://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import api

from extendable_pydantic import StrictExtendableBaseModel


class HelpdeskTicket(StrictExtendableBaseModel):

    # readonly
    id: int
    name: str | None = None # ticket name
    created_date: datetime | None = None

    # write / read
    partner_name: str | None = None
    partner_email: str | None = None

    description: str | None = None
    # sale_order_id: writable at creation (linked only if the authenticated
    # partner can see the sale order); sale_order_name: readonly
    sale_order_id: int | None = None
    sale_order_name: str | None = None
    # team_id: writable at creation (must be an existing team); team_name: readonly
    team_id: int | None = None
    team_name: str | None = None

    def to_helpdesk_ticket_vals(self) -> dict:
        return {
            #"from_api": True, todo: faire helpdesk.ticket.channel
            "name": self.name,
            "partner_name": self.partner_name or "",
            "partner_email": self.partner_email or "",
            "description": self.description,
            "sale_order_id": self.sale_order_id,
            "team_id": self.team_id,
        }

    @classmethod
    def from_helpdesk_ticket(cls, odoo_rec):
        # a ticket may have several linked sale orders, only the first one
        # is exposed here
        sale_order = odoo_rec.sale_order_ids[:1]
        return cls.model_construct(
            id=odoo_rec.id,
            name=odoo_rec.name,
            created_date=odoo_rec.create_date,
            description=odoo_rec.description or None,
            partner_name=odoo_rec.partner_name,
            partner_email=odoo_rec.partner_email,
            sale_order_id=sale_order.id or None,
            sale_order_name=sale_order.name or None,
            team_id=odoo_rec.team_id.id or None,
            team_name=odoo_rec.team_id.name or None,
        )


class HelpdeskMessage(StrictExtendableBaseModel):
    id: int
    create_date: datetime
    author: str | None = None
    body: str | None = None

    @classmethod
    def from_mail_message(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            create_date=odoo_rec.create_date,
            author=odoo_rec.author_id.sudo().display_name or odoo_rec.email_from,
            body=odoo_rec.body or None,
        )


class HelpdeskTicketWithDetail(HelpdeskTicket):

    messages: list[HelpdeskMessage]

    @classmethod
    def from_helpdesk_ticket(cls, odoo_rec):
        ticket = super().from_helpdesk_ticket(odoo_rec)
        # customer-facing chatter exchanges only, internal notes excluded
        # (same rule as mail.message._get_search_domain_share)
        chatter_messages = odoo_rec.message_ids.filtered(
            lambda m: not m.is_internal and m.subtype_id and not m.subtype_id.internal
        ).sorted("id")
        return cls.model_construct(
            **ticket.model_dump(),
            messages=[
                HelpdeskMessage.from_mail_message(m) for m in chatter_messages
            ],
        )

class HelpdeskTicketSearch(StrictExtendableBaseModel, extra="ignore"):
    def to_odoo_domain(self, env: api.Environment) -> list:
        domain = []
        return domain

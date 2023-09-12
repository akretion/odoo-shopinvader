from odoo.addons.extendable_fastapi import StrictExtendableBaseModel
from typing import List, Optional
from datetime import datetime

from extendable_pydantic import ExtendableBaseModel, ExtendableModelMeta
from pydantic import BaseModel, EmailStr, Field


class IdRequest(StrictExtendableBaseModel):
    id: int

    @classmethod
    def from_rec(cls, odoo_rec):
        if not odoo_rec:
            return
        return cls.model_construct(
            id=odoo_rec.id,
        )


class IdAndNameInfo(StrictExtendableBaseModel):
    id: int
    name: str | None = None

    @classmethod
    def from_rec(cls, odoo_rec):
        if not odoo_rec:
            return
        return cls.model_construct(
            id=odoo_rec.id,
            name=odoo_rec.name,
        )


class HelpdeskTicketSaleLineInfo(BaseModel):
    sale_line_id: int
    qty: int
    product_name: str = None

    @classmethod
    def from_sale_order_line(cls, sol):
        return cls.model_construct(
            sale_line_id=sol.id, qty=sol.qty, product_name=sol.product_name
        )


class HelpdeskTicketInfo(StrictExtendableBaseModel):
    id: int
    name: str
    description: str
    create_date: datetime
    last_stage_update: datetime
    category: IdAndNameInfo | None = Field(description="Category")
    team: IdAndNameInfo | None = Field(description="Team")
    stage: IdAndNameInfo = Field(description="Stage")

    sale: IdAndNameInfo | None = Field(description="Sale")
    sale_lines: List[HelpdeskTicketSaleLineInfo] = Field(description="Sale order lines")

    @classmethod
    def from_ticket(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            name=odoo_rec.name or None,
            description=odoo_rec.description or None,
            create_date=odoo_rec.create_date or None,
            last_stage_update=odoo_rec.last_stage_update or None,
            category=IdAndNameInfo.from_rec(odoo_rec.category_id),
            team=IdAndNameInfo.from_rec(odoo_rec.team_id),
            stage=IdAndNameInfo.from_rec(odoo_rec.stage_id),
            sale=IdAndNameInfo.from_rec(odoo_rec.sale_id),
            sale_lines=[
                HelpdeskTicketSaleLineInfo.from_sale_order_line(sol)
                for sol in odoo_rec.sale_line_ids
            ],
        )


class HelpdeskPartnerRequest(StrictExtendableBaseModel):
    email: EmailStr
    name: str
    lang: str = None


class HelpdeskTicketRequest(StrictExtendableBaseModel):
    name: str
    description: str
    partner: Optional[HelpdeskPartnerRequest] = Field(default=None)
    category: Optional[IdRequest] = Field(default=None)
    team: Optional[IdRequest] = Field(default=None)
    sale: Optional[IdRequest] = Field(default=None, alias="sale_id")

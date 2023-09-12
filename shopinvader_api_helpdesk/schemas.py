from odoo.addons.extendable_fastapi import StrictExtendableBaseModel
from typing import List
from datetime import datetime

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel, EmailStr, Field


# class IdAndNameInfo(StrictExtendableBaseModel):
#     id: int
#     name: str


class HelpdeskTicketInfo(StrictExtendableBaseModel):
    id: int
    name: str
    description: str
    create_date: datetime
    last_stage_update: datetime
    # category: IdAndNameInfo = Field(None, alias="category_id")
    # team: IdAndNameInfo = Field(None, alias="team_id")
    # stage: IdAndNameInfo = Field(None, alias="stage_id")

    # sale: IdAndNameInfo = Field(None, alias="sale_id")
    # sale_lines: List[HelpdeskTicketSaleLineInfo] = Field([], alias="sale_line_ids")

    @classmethod
    def from_ticket(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            name=odoo_rec.name or None,
            description=odoo_rec.description or None,
            create_date=odoo_rec.create_date or None,
            last_stage_update=odoo_rec.last_stage_update or None,
        )

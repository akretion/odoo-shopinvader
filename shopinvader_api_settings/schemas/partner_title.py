# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from extendable_pydantic import StrictExtendableBaseModel


class PartnerTitle(StrictExtendableBaseModel):
    id: int
    name: str

    @classmethod
    def from_res_partner_title(cls, odoo_rec):
        return cls.model_construct(id=odoo_rec.id, name=odoo_rec.name)

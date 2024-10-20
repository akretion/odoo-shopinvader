# Copyright 2024 Akretion France
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from extendable_pydantic import StrictExtendableBaseModel


class State(StrictExtendableBaseModel):
    id: int
    name: str
    code: str
    country: int

    @classmethod
    def from_res_country_state(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            name=odoo_rec.name,
            code=odoo_rec.code,
            country=odoo_rec.country_id.id,
        )

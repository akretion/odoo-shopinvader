# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.addons.shopinvader_schema_sale.schemas import BaseSale


class Sale(BaseSale):
    date_commitment: datetime | None = None

    @classmethod
    def from_sale_order(cls, odoo_rec):
        obj = super().from_sale_order(odoo_rec)
        obj.date_commitment = odoo_rec.commitment_date or None
        return obj

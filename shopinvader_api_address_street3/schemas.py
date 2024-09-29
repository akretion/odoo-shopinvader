# Copyright 2024 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_api_address.schemas import AddressCreate, AddressUpdate
from odoo.addons.shopinvader_schema_address.schemas import Address


class AddressCreateStreet3(AddressCreate, extends=True):

    street3: str | None = None

    def to_res_partner_vals(self) -> dict:
        vals = super().to_res_partner_vals()
        vals["street3"] = self.street3
        return vals


class AddressUpdateStreet3(AddressUpdate, extends=True):

    street3: str | None = None

    def to_res_partner_vals(self) -> dict:
        vals = super().to_res_partner_vals()
        vals["street3"] = self.street3
        return vals


class AddressStreet3(Address, extends=True):

    street3: str | None = None

    @classmethod
    def from_res_partner(cls, odoo_rec):
        obj = super().from_res_partner(odoo_rec)
        obj.street3 = odoo_rec.street3 or None
        return obj

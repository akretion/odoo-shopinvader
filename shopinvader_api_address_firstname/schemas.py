# Copyright 2024 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_api_address.schemas import AddressCreate, AddressUpdate
from odoo.addons.shopinvader_schema_address.schemas import Address


class AddressCreateFirstname(AddressCreate, extends=True):

    firstname: str | None = None
    lastname: str | None = None

    def to_res_partner_vals(self) -> dict:
        vals = super().to_res_partner_vals()
        vals["firstname"] = self.firstname
        vals["lastname"] = self.lastname
        return vals


class AddressUpdateFirstname(AddressUpdate, extends=True):

    firstname: str | None = None
    lastname: str | None = None

    def to_res_partner_vals(self) -> dict:
        vals = super().to_res_partner_vals()
        vals["firstname"] = self.firstname
        vals["lastname"] = self.lastname
        return vals


class AddressFirstname(Address, extends=True):

    firstname: str | None = None
    lastname: str | None = None

    @classmethod
    def from_res_partner(cls, odoo_rec):
        obj = super().from_res_partner(odoo_rec)
        obj.firstname = odoo_rec.firstname or None
        obj.lastname = odoo_rec.lastname or None
        return obj

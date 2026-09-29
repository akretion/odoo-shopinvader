# Copyright 2026 Akretion (http://www.akretion.com).
# @author Benoît Guillot <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_api_address.schemas import (
    AddressCreate as BaseAddressCreate,
)


class AddressCreate(BaseAddressCreate, extends=True):
    """Allow the customer to select a default directory line on its address."""

    einvoicing_directory_line: int | None = None

    def to_res_partner_vals(self) -> dict:
        vals = super().to_res_partner_vals()
        vals["default_fr_directory_line_id"] = self.einvoicing_directory_line
        return vals

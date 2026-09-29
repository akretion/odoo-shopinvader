# Copyright 2026 Akretion (http://www.akretion.com).
# @author Benoît Guillot <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_api_address.schemas import (
    AddressUpdate as BaseAddressUpdate,
)


class AddressUpdate(BaseAddressUpdate, extends=True):
    """Allow the customer to select a default directory line on its address.

    The field is set only when the customer sends it: a ``null`` value removes
    the selected line.
    """

    einvoicing_directory_line: int | None = None

    def to_res_partner_vals(self) -> dict:
        vals = super().to_res_partner_vals()
        values = self.model_dump(
            exclude_unset=True, include=["einvoicing_directory_line"]
        )
        if "einvoicing_directory_line" in values:
            vals["default_fr_directory_line_id"] = values["einvoicing_directory_line"]
        return vals

# Copyright 2026 Akretion (http://www.akretion.com).
# @author Benoît Guillot <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_schema_address.schemas import Address as BaseAddress

from .directory_line import DirectoryLine


class Address(BaseAddress, extends=True):
    """Add the French eInvoicing directory on the addresses of the API.

    The directory lines belong to the commercial entity of the account, so
    every address of an account exposes the same list. The default line can be
    selected on each address: the one of the address itself is exposed, with
    the one of the commercial entity as a fallback.
    """

    einvoicing_directory_line: DirectoryLine | None = None
    company_identifier: str | None = None

    @classmethod
    def from_res_partner(cls, odoo_rec):
        res = super().from_res_partner(odoo_rec)
        res.einvoicing_directory_line = DirectoryLine.from_fr_directory_line(
            odoo_rec._get_shopinvader_default_fr_directory_line()
        )
        res.company_identifier = odoo_rec.commercial_partner_id.siret
        return res

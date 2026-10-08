# Copyright 2026 Akretion (http://www.akretion.com).
# @author Benoît Guillot <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import Annotated

from fastapi import Depends

from odoo.addons.shopinvader_api_address.routers.addresses import (
    AddressHelper as BaseAddressHelper,
)
from odoo.addons.shopinvader_api_address.routers.addresses import (
    address_helper,
    address_router,
)
from odoo.addons.shopinvader_router_helper import VirtualModel

from ..schemas.directory_line import DirectoryLine, DirectoryLineSyncInput


class AddressHelper(VirtualModel):
    _inherit = "shopinvader_api_address.address_router.helper"

    def _sync_fr_directory_lines(
        self, company_identifier: str | None
    ) -> list[DirectoryLine]:
        """Sync the eInvoicing directory of the account and return its lines.

        The directory lines belong to the account of the authenticated partner
        (the main partner).
        """
        directory_lines = self.partner.sudo()._sync_shopinvader_fr_directory(
            company_identifier
        )
        return [
            DirectoryLine.from_fr_directory_line(directory_line)
            for directory_line in directory_lines
        ]


@address_router.post(
    "/einvoicing/directory_lines",
    response_model=list[DirectoryLine],
)
def sync_address_directory_lines(
    helper: Annotated[BaseAddressHelper, Depends(address_helper)],
    data: DirectoryLineSyncInput,
) -> list[DirectoryLine]:
    """Sync the French eInvoicing directory of the customer.

    Called by the front end when the customer sets its vat number: the vat is
    written on the account, the directory is queried and the directory lines
    which can be used as default line are returned.
    """
    return helper._sync_fr_directory_lines(data.company_identifier)

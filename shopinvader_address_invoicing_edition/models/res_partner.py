# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_shopinvader_invoicing_addresses(self) -> "ResPartner":
        self.ensure_one()
        invoicing_addresses = self.env["res.partner"].search(
            [("parent_id", "=", self.id), ("type", "=", "invoice")],
            order="id desc",
            limit=1,
        )
        return invoicing_addresses or self

    def _update_shopinvader_invoicing_address(
        self, vals: dict, address: "ResPartner"
    ) -> "ResPartner":
        self.ensure_one()
        if any(key in vals for key in ("parent_id", "type")):
            raise UserError(
                _(
                    "parent_id and type cannot be modified on "
                    "shopinvader invoicing address, id: %(address_id)d",
                    address_id=address.id,
                )
            )

        if self == address or (
            self.env["sale.order"]
            .sudo()
            .search(
                [
                    ("partner_invoice_id", "=", address.id),
                    ("state", "in", ("done", "sale")),
                ],
                limit=1,
            )
        ):
            # Create a new address instead of modifying the existing one
            vals.update(
                {
                    "parent_id": self.id,
                    "type": "invoice",
                }
            )
            new_address = self.env["res.partner"].create(vals)
            return new_address

        address.write(vals)

        return address

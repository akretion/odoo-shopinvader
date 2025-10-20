# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_shopinvader_invoicing_addresses(self) -> "ResPartner":
        if self.partner_invoice_id:
            return self.partner_invoice_id
        return super()._get_shopinvader_invoicing_addresses()

    def _update_shopinvader_invoicing_address(
        self, vals: dict, address: "ResPartner"
    ) -> "ResPartner":
        rv = super()._update_shopinvader_invoicing_address(vals, address)
        if self.partner_invoice_id == address and rv != address:
            self.partner_invoice_id = rv
        return rv

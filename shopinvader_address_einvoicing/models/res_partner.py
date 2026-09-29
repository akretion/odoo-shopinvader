# Copyright 2026 Akretion (http://www.akretion.com).
# @author Benoît Guillot <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_shopinvader_fr_directory_lines(self):
        """Return the eInvoicing directory lines of the account.

        The directory lines always belong to the commercial entity of the
        account, so every address of an account shares the same lines. They are
        sorted on the identifier to keep a stable order in the API responses.
        """
        self.ensure_one()
        return self.commercial_partner_id.fr_directory_line_ids.sorted(
            lambda directory_line: directory_line.identifier or ""
        )

    def _get_shopinvader_default_fr_directory_line(self):
        """Return the directory line used by default by the address.

        The line configured on the address itself wins over the one of the
        account: this is the way Odoo selects the directory line of an invoice.
        """
        self.ensure_one()
        return (
            self.default_fr_directory_line_id
            or self.commercial_partner_id.default_fr_directory_line_id
        )

    def _sync_shopinvader_fr_directory(self, vat=None):
        """Sync the eInvoicing directory of the account and return its lines.

        The directory is queried with the data of the account (the commercial
        entity), so the vat received from the customer is written on the
        account before the sync when it has been changed.
        """
        self.ensure_one()
        partner = self.commercial_partner_id
        if vat:
            # the vat is a commercial field: it always belongs to the account
            vat = "".join(vat.split()).upper()
            if partner.vat != vat:
                partner.write({"vat": vat})
        partner.fr_directory_sync_button()
        return partner._get_shopinvader_fr_directory_lines()

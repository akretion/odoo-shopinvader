# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def cron_update_gift_card_state(self):
        super().cron_update_gift_card_state()
        cards = self.search(
            [
                ("state", "in", ["active", "not_activated"]),
                "|",
                ("email_beneficiary_sent", "!=", True),
                ("email_buyer_sent", "!=", True),
            ]
        )
        for card in cards:
            if not card.email_buyer_sent:
                card.send_email_to_buyer()
            if card.state == "active" and not card.email_beneficiary_sent:
                card.send_email_to_beneficiary()

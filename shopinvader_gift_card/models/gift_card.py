# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class GiftCard(models.Model):
    _inherit = "gift.card"

    comment = fields.Text(string="Comment")
    beneficiary_name = fields.Char(string="Beneficiary Name")
    beneficiary_email = fields.Char(string="Beneficiary Email")
    buyer_name = fields.Char(string="Buyer Name")
    buyer_email = fields.Char(string="Buyer Email")
    email_beneficiary_sent = fields.Boolean(default=False)
    email_buyer_sent = fields.Boolean(default=False)
    shopinvader_backend_id = fields.Many2one(
        "shopinvader.backend", "Shopinvader Backend"
    )

    state = fields.Selection(
        selection_add=[("draft", "Draft")],
        ondelete={"draft": "set default"},
    )

    user_id = fields.Many2one(related="sale_id.user_id")

    def send_email_to_beneficiary(self):
        if self.shopinvader_backend_id:
            self.shopinvader_backend_id._send_notification("gift_card_activated", self)
            self.email_beneficiary_sent = True

    def send_email_to_buyer(self):
        if self.shopinvader_backend_id:
            self.shopinvader_backend_id._send_notification("gift_card_created", self)
            self.email_buyer_sent = True

    @api.model
    def cron_update_gift_card_state(self):
        super().cron_update_gift_card_state()
        cards = self.search(
            [
                ("state", "in", ["active", "not_activated"]),
                ("shopinvader_backend_id", "!=", False),
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

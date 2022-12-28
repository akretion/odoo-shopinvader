# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


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

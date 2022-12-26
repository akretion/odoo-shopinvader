# Copyright 2022 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    gift_cards = env["gift.card"].search([])
    for card in gift_cards:
        if card.invoice_id.state != "draft":
            card.email_buyer_sent = True
        if card.state == "active":
            card.email_beneficiary_sent = True

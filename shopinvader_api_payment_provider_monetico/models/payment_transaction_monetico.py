# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from urllib.parse import urljoin

from odoo import models


class PaymentTransactionMonetico(models.Model):
    _inherit = "payment.transaction"

    def _monetico_form_presign_hook(self, values):
        """Insert shopinvader return url in the form values"""
        shopinvader_api_payment = self.env.context.get("shopinvader_api_payment")
        values = super()._monetico_form_presign_hook(values)

        if not shopinvader_api_payment:
            return values

        shopinvader_api_payment_base_url = self.env.context.get(
            "shopinvader_api_payment_base_url"
        )
        values["url_return_ok"] = values["url_return_err"] = urljoin(
            shopinvader_api_payment_base_url, "monetico/return"
        )

        # Where?
        # shopinvader_api_payment_frontend_redirect_url = self.env.context.get(
        #     "shopinvader_api_payment_frontend_redirect_url"
        # )

        return values

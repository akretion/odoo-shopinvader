# Copyright 2024 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from urllib.parse import urljoin

from odoo import models


class PaymentTransactionsPaybox(models.Model):
    _inherit = "payment.acquirer"

    def paybox_form_generate_values(self, processing_values):
        """
        Override of payment to return Paybox-specific rendering values.
        Update the Odoo url values, and then re-sign the response


        """

        shopinvader_api_payment = self.env.context.get(
            "shopinvader_api_payment"
        )

        res = super().paybox_form_generate_values(processing_values)

        if self.provider != "paybox" or not shopinvader_api_payment:
            return res

        shopinvader_api_payment_base_url = self.env.context.get(
            "shopinvader_api_payment_base_url"
        )

        res["PBX_EFFECTUE"] = urljoin(
            shopinvader_api_payment_base_url,
            "paybox/return"
        )
        res["PBX_ANNULE"] = urljoin(
            shopinvader_api_payment_base_url,
            "paybox/return"
        )
        res["PBX_REFUSE"] = urljoin(
            shopinvader_api_payment_base_url,
            "paybox/return"
        )
        res["PBX_ATTENTE"] = urljoin(
            shopinvader_api_payment_base_url,
            "paybox/return"
        )
        res["PBX_REPONDRE_A"] = urljoin(
            shopinvader_api_payment_base_url,
            "paybox/webhook"
        )

        del res["PBX_HMAC"]
        res["PBX_HMAC"] = self._paybox_generate_hmacsign(res).upper()
        return res

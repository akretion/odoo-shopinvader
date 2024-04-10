# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from urllib.parse import urljoin

from odoo import models


class PaymentTransactionSystempay(models.Model):
    _inherit = "payment.transaction"

    def systempay_form_generate_values(self, processing_values):
        """Override of payment to return Systempay-specific rendering values.
        Update the Odoo url values, and then re-sign the response

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific
        processing values of the transaction
        :return: The dict of provider-specific processing values
        :rtype: dict
        """
        shopinvader_api_payment = self.env.context.get("shopinvader_api_payment")

        res = super().sips_form_generate_values(processing_values)

        if self.provider != "systempay" or not shopinvader_api_payment:
            return res

        shopinvader_api_payment_frontend_redirect_url = self.env.context.get(
            "shopinvader_api_payment_frontend_redirect_url"
        )
        shopinvader_api_payment_base_url = self.env.context.get(
            "shopinvader_api_payment_base_url"
        )

        res["vads_url_return"] = urljoin(
            shopinvader_api_payment_base_url, "systempay/return"
        )
        # Needed?
        res["vads_url_check"] = urljoin(
            shopinvader_api_payment_base_url, "systempay/webhook"
        )
        # FIXME: Check this
        res["vads_ext_info_reference"] = processing_values["reference"]
        res[
            "vads_ext_info_redirect_url"
        ] = shopinvader_api_payment_frontend_redirect_url

        del res["systempay_signature"]
        res["systempay_signature"] = self._systempay_generate_sign(self, res)
        return res

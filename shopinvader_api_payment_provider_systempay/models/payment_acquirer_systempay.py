# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from urllib.parse import urljoin

from odoo import models
from odoo.http import WebRequest, request


class FakeSession:
    def __init__(self):
        self.db = None
        self.uid = None


class FakeRequest:
    def __init__(self, base_url):
        self.host_url = base_url
        self.session = FakeSession()


class AcquirerSystempay(models.Model):
    _inherit = "payment.acquirer"

    def systempay_form_generate_values(self, values):
        """Override of payment to return Systempay-specific rendering values.
        Update the Odoo url values, and then re-sign the response

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific
        processing values of the transaction
        :return: The dict of provider-specific processing values
        :rtype: dict
        """
        try:
            request._get_current_object()
        except RuntimeError:
            # We need to create a fake request for the payment_systempay module
            # since it gets the base url from the request object directly
            fake_werkzeug_request = FakeRequest(
                self.env["ir.config_parameter"].get_param("web.base.url")
            )
            fake_request = WebRequest(fake_werkzeug_request)
            with fake_request:
                res = super().systempay_form_generate_values(values)
        else:
            res = super().systempay_form_generate_values(values)

        shopinvader_api_payment = self.env.context.get("shopinvader_api_payment")

        if self.provider != "systempay" or not shopinvader_api_payment:
            return res

        shopinvader_api_payment_base_url = self.env.context.get(
            "shopinvader_api_payment_base_url"
        )
        res["vads_url_return"] = urljoin(
            shopinvader_api_payment_base_url, "systempay/return"
        )

        del res["systempay_signature"]
        res["systempay_signature"] = self._systempay_generate_sign(
            self,
            {
                key: value.decode("utf-8") if isinstance(value, bytes) else value
                for key, value in res.items()
            },
        )
        return res

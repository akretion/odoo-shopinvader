# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


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
                return super().systempay_form_generate_values(values)

        return super().systempay_form_generate_values(values)

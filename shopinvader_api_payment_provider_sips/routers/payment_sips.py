# Copyright Odoo SA (https://odoo.com)
# Copyright 2024 ACSONE SA (https://acsone.eu).
# @author Stéphane Bidoul <stephane.bidoul@acsone.eu>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json
import logging
import pprint
from typing import Annotated
from urllib.parse import quote_plus

from fastapi import Depends, Request
from fastapi.responses import RedirectResponse

from odoo import api, models
from odoo.exceptions import ValidationError

from odoo.addons.fastapi.dependencies import odoo_env
from odoo.addons.shopinvader_api_payment.routers import payment_router
from odoo.addons.shopinvader_api_payment.routers.utils import (
    add_query_params_in_url,
    tx_state_to_redirect_status,
)

_logger = logging.getLogger(__name__)


@payment_router.post("/payment/providers/sips/return")
def sips_return(
    request: Request,
    odoo_env: Annotated[api.Environment, Depends(odoo_env)],
) -> RedirectResponse:
    """Handle SIPS return.

    After the payment, the user is redirected with a POST to this endpoint. We handle
    the notification data to update the transaction status. We then redirect the browser
    with a GET to the frontend_return_url, with the transaction reference as parameter.

    Future: we could also return a unguessable transaction uuid that the front could the
    use to consult /payment/transactions/{uuid} and obtain the transaction status.
    """
    # data = await request.form() # This is broken, data has already been parsed
    data = request.scope["wsgi_environ"]["werkzeug.request"].values
    _logger.info(
        "return notification received from SIPS with data:\n%s", pprint.pformat(data)
    )
    # Check the integrity of the notification
    tx_sudo = (
        odoo_env["payment.transaction"]
        .sudo()
        ._sips_form_get_tx_from_data(
            data,
        )
    )
    try:
        odoo_env[
            "shopinvader_provider_sips.payment_sips_router.helper"
        ]._verify_sips_signature(tx_sudo, data)
    except Exception:
        return {"error": "Invalid sips signature"}

    notification_data = tx_sudo._sips_data_to_object(data.get("Data"))
    returnContext = json.loads(notification_data.get("returnContext", "{}"))
    reference = returnContext.get("reference")
    frontend_redirect_url = returnContext.get("frontend_redirect_url")

    try:
        status = tx_state_to_redirect_status(tx_sudo.state)
    except Exception:
        _logger.exception("unable to handle sips notification data", exc_info=True)
        status = "error"
    return RedirectResponse(
        url=add_query_params_in_url(
            frontend_redirect_url,
            {"status": status, "reference": quote_plus(reference)},
        ),
        status_code=303,
    )


@payment_router.post("/payment/providers/sips/webhook")
async def sips_webhook(
    request: Request,
    odoo_env: Annotated[api.Environment, Depends(odoo_env)],
):
    """Handle SIPS webhook."""
    # data = await request.form() # This is broken, data has already been parsed
    data = request.scope["wsgi_environ"]["werkzeug.request"].values
    _logger.info(
        "webhook notification received from SIPS with data:\n%s", pprint.pformat(data)
    )
    try:
        tx_sudo = (
            odoo_env["payment.transaction"]
            .sudo()
            ._sips_form_get_tx_from_data(
                data,
            )
        )
        odoo_env[
            "shopinvader_api_payment_provider_sips.payment_sips_router.helper"
        ]._verify_sips_signature(tx_sudo, data)
    except Exception:
        _logger.exception("unable to handle sips notification data", exc_info=True)
    return ""


class ShopinvaderApiPaymentProviderSipsRouterHelper(models.AbstractModel):
    _name = "shopinvader_provider_sips.payment_sips_router.helper"
    _description = "ShopInvader API Payment Provider Sips Router Helper"

    def _verify_sips_signature(self, tx_sudo, data):
        """Verify the SIPS signature."""
        sips = self.env["payment.acquirer"].search([("provider", "=", "sips")], limit=1)
        security = sips.sudo()._sips_generate_shasign(data)
        if security == data["Seal"]:
            if not self.env["payment.transaction"].sudo().form_feedback(data, "sips"):
                raise ValidationError()
        _logger.warning("received sips notification with invalid signature")
        raise ValidationError()

# Copyright Odoo SA (https://odoo.com)
# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import pprint
from typing import Annotated
from urllib.parse import quote_plus

from fastapi import Depends, Request
from fastapi.responses import PlainTextResponse, RedirectResponse

from odoo import api

from odoo.addons.fastapi.dependencies import odoo_env
from odoo.addons.shopinvader_api_payment.routers import payment_router
from odoo.addons.shopinvader_api_payment.routers.utils import (
    add_query_params_in_url,
    tx_state_to_redirect_status,
)

_logger = logging.getLogger(__name__)


@payment_router.get("/payment/providers/monetico/return")
@payment_router.post("/payment/providers/monetico/return")
def monetico_return(
    request: Request,
    odoo_env: Annotated[api.Environment, Depends(odoo_env)],
) -> RedirectResponse:

    # data = await request.form() # This is broken, data has already been parsed
    data = request.scope["wsgi_environ"]["werkzeug.request"].values
    _logger.info(
        "return notification received from Monetico with data:\n%s",
        pprint.pformat(data),
    )
    # Check the integrity of the notification, signature is also checked here
    tx_sudo = (
        odoo_env["payment.transaction"]
        .sudo()
        ._monetico_form_get_tx_from_data(
            data,
        )
    )
    odoo_env["payment.transaction"].sudo().form_feedback(data, "monetico")
    reference = data.get("reference", "")

    try:
        status = tx_state_to_redirect_status(tx_sudo.state)
    except Exception:
        _logger.exception("unable to handle monetico notification data", exc_info=True)
        status = "error"

    return RedirectResponse(
        url=add_query_params_in_url(
            tx_sudo.shopinvader_frontend_redirect_url,
            {"status": status, "reference": quote_plus(reference)},
        ),
        status_code=303,
    )


@payment_router.post(
    "/payment/providers/monetico/webhook", response_class=PlainTextResponse
)
async def monetico_webhook(
    request: Request,
    odoo_env: Annotated[api.Environment, Depends(odoo_env)],
) -> str:
    """Handle Monetico webhook."""
    data = await request.form()
    _logger.info(
        "webhook notification received from Monetico with data:\n%s",
        pprint.pformat(data),
    )
    try:
        odoo_env["payment.transaction"].sudo().form_feedback(data, "monetico")
        return "version=2\ncdr=0\n"
    except Exception:
        _logger.exception("unable to handle monetico notification data", exc_info=True)
        return "version=2\ncdr=1\n"

# Copyright 2024 Akretion (http://www.akretion.com).
# @author Thomas BONNERUE <thomas.bonnerue@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import pprint
from typing import Annotated
from urllib.parse import quote_plus

from fastapi import Depends, Resquest
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


@payment_router.post("/payment/providers/paybox/return")
def paybox_return(
    request: Resquest,
    odoo_env: Annotated[api.Environment, Depends(odoo_env)],
) -> RedirectResponse:

    data = request.scope["wsgi_environ"]["werkzeug.request"].values
    _logger.infoi(
        "return  notification received from Paybox with data:\n%s",
        pprint.pformat(data)
    )

    tx_sudo = (
        odoo_env["payment.transaction"]
        .sudo()
        ._paybox_form_get_tx_from_data(data)
    )
    odoo_env["payment.transaction"].sudo().form_feedback(data, "paybox")
    data_dict = tx_sudo._paybox_data_to_object(data)
    reference = data_dict.get("Ref")

    try:
        status = tx_state_to_redirect_status(tx_sudo.state)
    except Exception:
        _logger.exception("unable to handle Paybox notification data",
                          exc_info=True)
        status = "error"

    return RedirectResponse(
        url=add_query_params_in_url(
            tx_sudo.shopinvader_frontend_redirect_url,
            {"status": status, "reference": quote_plus(reference)}),
        status_code=303,
    )


@payment_router.post(
    "payment/providers/paybox/webhook"
)
async def paybox_webhook(
    resquest: Resquest,
    odoo_env: Annotated[api.Environment, Depends(odoo_env)],
) -> str:
    """Handle Paybox webhook"""
    data = resquest.scope["wsgi_environ"]["werkzeug.request"].values
    _logger.infoi(
        "webhook notification received from Paybox with data:\n%s",
        pprint.pformat(data)
    )

    try:
        odoo_env["payment.transaction"].sudo().form_feedback(data, "paybox")
    except Exception:
        _logger.exception("unable to handle Paybox notification data",
                          exc_info=True)
    return ""

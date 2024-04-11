# Copyright Odoo SA (https://odoo.com)
# Copyright 2024 ACSONE SA (https://acsone.eu).
# @author Stéphane Bidoul <stephane.bidoul@acsone.eu>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from typing import Annotated, Any
from urllib.parse import urljoin

from fastapi import APIRouter, Depends, HTTPException, Request

from odoo import api, models
from odoo.tools.misc import format_amount

from odoo.addons.fastapi.dependencies import odoo_env
from odoo.addons.payment.models.payment_acquirer import (
    PaymentAcquirer as PaymentProvider,
    PaymentTransaction,
)

from ..schemas import (
    PaymentDataWithMethods,
    PaymentProvider as PaymentProviderSchema,
    TransactionCreate,
    TransactionProcessingValues,
)
from .utils import Payable

_logger = logging.getLogger(__name__)

payment_router = APIRouter(tags=["payment"])


@payment_router.get("/payment/methods")
def pay(
    payable: str,
    odoo_env: Annotated[api.Environment, Depends(odoo_env)],
) -> PaymentDataWithMethods:
    """Available payment providers for the given encoded payment data.

    This route is public, so it is possible to pay anonymously provided that the
    parameters are obtained securely by another mean. An authenticated user can
    obtain the parameters with corresponding routes on the related payable
    objects (/cart/current/payable for e.g.).
    """
    try:
        payable_obj = Payable.decode(odoo_env, payable)
    except Exception as e:
        _logger.info("Could not decode payable")
        raise HTTPException(403) from e
    # This method is similar to Odoo's PaymentPortal.payment_pay
    providers_sudo = (
        odoo_env["payment.acquirer"]
        .sudo()
        ._get_available_payment_input(
            company=odoo_env["res.company"].browse(payable_obj.company_id),
            partner=odoo_env["res.partner"].browse(payable_obj.partner_id),
        )
    )["acquirers"]
    return PaymentDataWithMethods(
        payable=payable,
        payable_reference=payable_obj.payable_reference,
        amount=payable_obj.amount,
        currency_code=odoo_env["res.currency"].browse(payable_obj.currency_id).name,
        amount_formatted=format_amount(
            odoo_env,
            payable_obj.amount,
            odoo_env["sale.order"].sudo().browse(payable_obj.payable_id).currency_id,
        ),
        providers=[
            PaymentProviderSchema.from_payment_provider(provider)
            for provider in providers_sudo
        ],
    )


@payment_router.post("/payment/transactions")
def transaction(
    data: TransactionCreate,
    request: Request,
    odoo_env: Annotated[api.Environment, Depends(odoo_env)],
) -> TransactionProcessingValues:
    """Create a payment transaction.

    Input is data obtained from /payment/providers, with the provider selected by the
    user. This route is public, so it is possible to pay anonymously.

    This route will automatically redirect to the return route linked to
    the specified provider. The user will finally land on data.frontend_redirect_url
    """
    try:
        payable_obj = Payable.decode(odoo_env, data.payable)
    except Exception as e:
        _logger.info("Could not decode payable")
        raise HTTPException(403) from e
    # similar to Odoo's /payment/transaction route
    if data.flow == "redirect":
        providers_sudo = (
            odoo_env["payment.acquirer"]
            .sudo()
            ._get_available_payment_input(
                company=odoo_env["res.company"].browse(payable_obj.company_id),
                partner=odoo_env["res.partner"].browse(payable_obj.partner_id),
            )
        )["acquirers"]
        if not data.provider_id or data.provider_id not in providers_sudo.ids:
            _logger.info(
                "Invalid provider %s for partner %s",
                data.provider_id,
                payable_obj.partner_id,
            )
            raise HTTPException(403)
        provider_sudo = odoo_env["payment.acquirer"].sudo().browse(data.provider_id)

        # Create the transaction
        tx_sudo = odoo_env[
            "shopinvader_api_payment.payment_router.helper"
        ]._create_transaction(data, provider_sudo, request, odoo_env)
        tx_sudo._log_payment_transaction_sent()

        transaction_processing_values = odoo_env[
            "shopinvader_api_payment.payment_router.helper"
        ]._get_tx_processing_values(
            tx_sudo,
            payable=data.payable,
            frontend_redirect_url=data.frontend_redirect_url,
        )
        return transaction_processing_values
    else:
        raise NotImplementedError("Only redirect flow is supported")


class ShopinvaderApiPaymentRouterHelper(models.AbstractModel):
    _name = "shopinvader_api_payment.payment_router.helper"
    _description = "ShopInvader API Payment Router Helper"

    def _get_additional_transaction_create_values(
        self,
        data: TransactionCreate,
        odoo_env: Annotated[api.Environment, Depends(odoo_env)],
    ) -> dict:
        # Intended to be extended for invoices, carts...
        additional_transaction_create_values = {}
        return additional_transaction_create_values

    def _get_tx_create_values(
        self,
        data: TransactionCreate,
        provider_sudo: PaymentProvider,
        odoo_env: Annotated[api.Environment, Depends(odoo_env)],
    ) -> dict:
        try:
            payable_obj = Payable.decode(odoo_env, data.payable)
        except Exception as e:
            _logger.info("Could not decode payable")
            raise HTTPException(403) from e
        additional_transaction_create_values = (
            self._get_additional_transaction_create_values(data, odoo_env)
        )

        is_validation = False  # future
        # compute transaction reference from payable reference
        tx_reference = (
            odoo_env["payment.transaction"]
            .sudo()
            ._compute_reference(
                # provider_code=provider_sudo.provider, # Not in v14.0
                prefix=payable_obj.payable_reference,
                values={
                    "acquirer_id": provider_sudo.id,
                    "partner_id": payable_obj.partner_id,
                },
                # TODO are custom_create_values and kwargs really needed
                # **(custom_create_values or {}),
                # **kwargs
            )
        )

        return {
            "acquirer_id": data.provider_id,
            "reference": tx_reference,
            "amount": payable_obj.amount,
            "currency_id": payable_obj.currency_id,
            "partner_id": payable_obj.partner_id,
            # 'token_id': token_id,
            # "operation": f"online_{data.flow}" if not is_validation else "validation",
            # "tokenize": False,
            "type": "form" if not is_validation else "validation",
            "shopinvader_frontend_redirect_url": data.frontend_redirect_url,
            **additional_transaction_create_values,
        }

    def _create_transaction(
        self,
        data: TransactionCreate,
        provider_sudo: PaymentProvider,
        request: Request,
        odoo_env: Annotated[api.Environment, Depends(odoo_env)],
    ) -> dict:
        transaction_values = odoo_env[
            "shopinvader_api_payment.payment_router.helper"
        ]._get_tx_create_values(data, provider_sudo, odoo_env)
        tx_sudo = (
            odoo_env["payment.transaction"]
            .sudo()
            .with_context(
                shopinvader_api_payment=True,
                shopinvader_api_payment_frontend_redirect_url=data.frontend_redirect_url,
                shopinvader_api_payment_base_url=urljoin(
                    str(request.url), "providers/"
                ),
            )
            .create(transaction_values)
        )
        return tx_sudo

    def _get_tx_processing_values(
        self, tx_sudo: PaymentTransaction, **kwargs: Any
    ) -> TransactionProcessingValues:
        """
        Extract the creation of the response to allow to extend it.
        """
        # There's no _get_processing_values in v14.0, so we fill it manually
        redirect_form_html = tx_sudo.acquirer_id.render(
            reference=tx_sudo.reference,
            amount=tx_sudo.amount,
            currency_id=tx_sudo.currency_id.id,
            partner_id=tx_sudo.partner_id.id,
            values={
                "partner_id": tx_sudo.partner_id.id,
                "type": "form",
            },
        )

        return TransactionProcessingValues(
            flow="redirect",
            provider_id=tx_sudo.acquirer_id.id,
            provider_code=tx_sudo.acquirer_id.provider,
            reference=tx_sudo.reference,
            amount=tx_sudo.amount,
            currency_id=tx_sudo.currency_id.id,
            partner_id=tx_sudo.partner_id.id,
            redirect_form_html=redirect_form_html,
        )

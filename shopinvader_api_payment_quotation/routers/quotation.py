# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import Annotated

from fastapi import Depends, HTTPException

from odoo import api
from odoo.exceptions import UserError
from odoo.tools.misc import format_amount

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)
from odoo.addons.shopinvader_api_payment.routers.utils import Payable
from odoo.addons.shopinvader_api_payment.schemas import PaymentData
from odoo.addons.shopinvader_api_quotation.routers.quotation import quotation_router


@quotation_router.get("/quotations/{quotation_id}/payable")
def quotation_payable(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated["ResPartner", Depends(authenticated_partner)],
    quotation_id: int,
) -> PaymentData:
    quotation = (
        env["shopinvader_api_quotation.router.helper"]
        .new({"partner": partner})
        ._get(quotation_id)
    )

    if not quotation:
        raise HTTPException(status_code=404)

    if quotation.quotation_state != "waiting_acceptation":
        raise UserError("Quotation is not in waiting acceptation state")

    payment_data = {
        "payable": Payable(
            payable_id=quotation.id,
            payable_model="sale.order",
            payable_reference=quotation.name,
            amount=quotation.amount_total,
            currency_id=quotation.currency_id.id,
            partner_id=quotation.partner_id.id,
            company_id=quotation.company_id.id,
        ).encode(env),
        "payable_reference": quotation.name,
        "amount": quotation.amount_total,
        "currency_code": quotation.currency_id.name,
        "amount_formatted": format_amount(
            env, quotation.amount_total, quotation.currency_id
        ),
    }
    return PaymentData(**payment_data)

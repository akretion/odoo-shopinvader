# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import Annotated

from fastapi import APIRouter, Depends

from odoo import api, fields, models

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)

from ..schemas.customer import Customer, CustomerUpdate

# create a router
customer_router = APIRouter(tags=["customer"])


@customer_router.get("/customer")
def get_customer_data(
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> Customer:
    """
    Get customer personal data of authenticated user
    """
    return Customer.from_res_partner(partner)


@customer_router.post(
    "/customer",
)
def update_customer_data(
    data: CustomerUpdate,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> Customer:
    """
    update customer personal data of authenticated user
    """
    CustomerUpdate.to_res_partner_vals(data)
    helper = env["shopinvader_api_customer.router.helper"].new({"partner": partner})
    updated_partner = helper._update_shopinvader_customer(data)
    return Customer.from_res_partner(updated_partner)


class ShopInvaderApiCustomerHelper(models.AbstractModel):
    _name = "shopinvader_api_customer.router.helper"
    _description = "API Customer Router Helper"

    partner = fields.Many2one(
        comodel_name="res.partner",
    )

    def _update_shopinvader_customer(self, data: CustomerUpdate) -> ResPartner:
        self.ensure_one()
        values = CustomerUpdate.to_res_partner_vals(data)
        lang_id = data.lang_id
        if bool(lang_id):
            values["lang"] = self.env["res.lang"].browse(lang_id).code
        partner = self.partner
        partner.write(values)
        self._handle_shopinvader_customer_opt_in(data)
        return partner

    def _handle_shopinvader_customer_opt_in(self, data):
        self.ensure_one()
        opt_in = data.opt_in
        if opt_in is None:
            return
        Blacklist = self.env["mail.blacklist"].sudo()
        partner = self.partner
        email = partner.email
        if not opt_in:
            Blacklist._add(email)
        else:
            Blacklist._remove(email)
        # as we return current partner data when updating,
        # we have to recompute is_blacklisted value ourselves
        partner._compute_is_blacklisted()

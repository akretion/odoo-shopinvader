# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from odoo import _, api, models
from odoo.exceptions import UserError

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)
from odoo.addons.sale.models.sale import SaleOrder
from odoo.addons.shopinvader_api_cart.schemas import CartTransaction

from ..schemas import CouponInput, Sale

sale_loyalty_cart_router = APIRouter(tags=["carts"])


@sale_loyalty_cart_router.post("/apply_coupon/{uuid}", deprecated=True)
@sale_loyalty_cart_router.post("/apply_coupon", deprecated=True)
@sale_loyalty_cart_router.post("/{uuid}/coupon")
@sale_loyalty_cart_router.post("/current/coupon")
@sale_loyalty_cart_router.post("/coupon")
def apply_coupon(
    data: CouponInput,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    uuid: UUID | None = None,
) -> Sale | None:
    """
    Apply a coupon on a specific cart.

    One can specify in LoyaltyCartInput which reward to choose, and
    which free product to choose.
    If some info is missing to uniquely determine which reward to apply,
    raise an error.
    """
    cart = env["sale.order"]._find_open_cart(partner.id, str(uuid) if uuid else None)
    if cart:
        env["shopinvader_api_cart.cart_router.helper"]._apply_coupon(cart, data)
    return Sale.from_sale_order(cart) if cart else None


class ShopinvaderApiCartRouterHelper(models.AbstractModel):
    _inherit = "shopinvader_api_cart.cart_router.helper"

    @api.model
    def _apply_coupon(self, cart: "SaleOrder", data: CouponInput):
        """Apply a coupon or promotion code.

        It can raise UserError if coupon is not applicable, or
        if the coupon let the choice between several rewards, and the
        selected reward is not specified.
        """
        (
            self.env["sale.coupon.apply.code"]
            .with_context(active_id=cart.id)
            .create({"coupon_code": data.code})
            .sudo()
            .process_coupon()
        )
        return cart

    @api.model
    def _sync_cart(
        self,
        partner: ResPartner,
        cart: SaleOrder,
        uuid: str,
        transactions: list[CartTransaction],
    ):
        cart = super()._sync_cart(partner, cart, uuid, transactions)

        if cart:
            cart.recompute_coupon_lines()

        return cart

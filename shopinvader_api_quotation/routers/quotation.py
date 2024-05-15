from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, StreamingResponse

from odoo import models
from odoo.api import Environment
from odoo.http import content_disposition

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.extendable_fastapi.schemas import PagedCollection
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
    paging,
)
from odoo.addons.fastapi.schemas import Paging
from odoo.addons.shopinvader_schema_sale.schemas.sale import Sale, SaleSearch

from ..schemas.sale import QuotationConfirmInput, QuotationUpdateInput

# create a router
quotation_router = APIRouter(tags=["quotations"])


@quotation_router.get("/quotations/{quotation_id}")
def get(
    env: Annotated[Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    quotation_id: int,
) -> Sale | None:
    return Sale.from_sale_order(
        env["shopinvader_api_quotation.quotations_router.helper"]
        .new({"partner": partner})
        ._get(quotation_id)
    )


@quotation_router.post("/quotations/{quotation_id}/confirm", status_code=200)
def confirm_quotation(
    env: Annotated[Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    quotation_id: int,
    data: QuotationConfirmInput | None = None,
) -> None:
    order = (
        env["shopinvader_api_quotation.quotations_router.helper"]
        .new({"partner": partner})
        ._confirm(quotation_id, data)
    )
    return Sale.from_sale_order(order)


@quotation_router.get("/quotations", status_code=200)
def search_quotation(
    params: Annotated[SaleSearch, Depends()],
    paging: Annotated[Paging, Depends(paging)],
    env: Annotated[Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> PagedCollection[Sale]:
    count, orders = (
        env["shopinvader_api_quotation.quotations_router.helper"]
        .new({"partner": partner})
        ._search(paging, params)
    )
    return PagedCollection[Sale](
        count=count,
        items=[Sale.from_sale_order(order) for order in orders],
    )


@quotation_router.post("/quotations/{quotation_id}")
def update_quotation(
    data: QuotationUpdateInput,
    env: Annotated[Environment, Depends(authenticated_partner_env)],
    partner: Annotated["ResPartner", Depends(authenticated_partner)],
    quotation_id: int,
) -> Sale:
    order = (
        env["shopinvader_api_quotation.quotations_router.helper"]
        .new({"partner": partner})
        ._update(quotation_id, data)
    )
    return Sale.from_sale_order(order)


@quotation_router.get("/quotations/{quotation_id}/download")
def download(
    quotation_id: int,
    env: Annotated[Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> FileResponse:
    """Download document."""
    filename, pdf = (
        env["shopinvader_api_quotation.quotations_router.helper"]
        .new({"partner": partner})
        ._get_pdf(quotation_id)
    )
    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"
    header = {
        "Content-Disposition": content_disposition(filename),
    }

    def pseudo_stream():
        yield pdf

    return StreamingResponse(
        pseudo_stream(), headers=header, media_type="application/pdf"
    )


class ShopinvaderApiSaleSalesRouterHelper(models.AbstractModel):
    _name = "shopinvader_api_quotation.quotations_router.helper"
    _inherit = "shopinvader_api_sale.sales_router.helper"
    _description = "Shopinvader api sale router helper"

    def _get_domain_adapter(self):
        return [
            ("partner_id", "=", self.partner.id),
            ("quotation_state", "in", ("customer_request", "waiting_acceptation")),
        ]

    def _process_confirm_quotation(self, quotation, data):
        """Process the quotation confirmation
        Can be inherited if you expect specific params
        for confirming a quotation"""
        return quotation.action_confirm_quotation()

    def _confirm(self, quotation_id, data):
        quotation = self._get(quotation_id)
        self._process_confirm_quotation(quotation, data)
        return quotation

    def _update(self, quotation_id, data):
        quotation = self._get(quotation_id)
        quotation.write(data.to_sale_order_vals())
        return quotation

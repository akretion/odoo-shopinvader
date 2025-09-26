# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, StreamingResponse

from odoo import api, fields, models
from odoo.http import content_disposition

from odoo.addons.account.models.account_move import AccountMove
from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.extendable_fastapi.schemas import PagedCollection
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
    paging,
)
from odoo.addons.fastapi.schemas import Paging
from odoo.addons.shopinvader_filtered_model.utils import FilteredModelAdapter
from odoo.addons.shopinvader_schema_invoice.schemas import Invoice, InvoiceSearch

invoice_router = APIRouter(tags=["invoices"])


@invoice_router.get("/invoices")
def search(
    params: Annotated[InvoiceSearch, Depends()],
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    paging: Annotated[Paging, Depends(paging)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> PagedCollection[Invoice]:
    """Get the list of current partner's invoices"""
    count, invoices = (
        env["shopinvader_api_invoice.invoices_router.helper"]
        .new({"partner": partner})
        ._search(paging, params)
    )
    return PagedCollection[Invoice](
        count=count,
        items=[Invoice.from_account_move(invoice) for invoice in invoices],
    )


@invoice_router.get("/invoices/{invoice_id}")
def get(
    invoice_id: int,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> Invoice:
    """
    Get the invoice of authenticated user with specific invoice_id
    """
    return Invoice.from_account_move(
        env["shopinvader_api_invoice.invoices_router.helper"]
        .new({"partner": partner})
        ._get(invoice_id)
    )


@invoice_router.get("/invoices/{invoice_id}/download")
def download(
    invoice_id: int,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> FileResponse:
    """Download document."""
    filename, pdf = (
        env["shopinvader_api_invoice.invoices_router.helper"]
        .new({"partner": partner})
        ._get_pdf(invoice_id)
    )
    header = {
        "Content-Disposition": content_disposition(filename),
    }

    def pseudo_stream():
        yield pdf

    return StreamingResponse(
        pseudo_stream(), headers=header, media_type="application/pdf"
    )


class ShopinvaderApiInvoiceInvoicesRouterHelper(models.AbstractModel):
    _name = "shopinvader_api_invoice.invoices_router.helper"
    _description = "Shopinvader Api Invoice Service Helper"

    partner = fields.Many2one("res.partner")

    def _get_domain_adapter(self):
        return [
            ("partner_id", "=", self.partner.id),
            ("move_type", "in", ("out_invoice", "out_refund")),
            ("state", "not in", ("cancel", "draft")),
        ]

    @property
    def model_adapter(self) -> FilteredModelAdapter[AccountMove]:
        return FilteredModelAdapter[AccountMove](self.env, self._get_domain_adapter())

    def _get(self, record_id) -> AccountMove:
        return self.model_adapter.get(record_id)

    def _search(self, paging, params) -> tuple[int, AccountMove]:
        return self.model_adapter.search_with_count(
            params.to_odoo_domain(self.env),
            limit=paging.limit,
            offset=paging.offset,
        )

    def _get_pdf(self, record_id) -> tuple[str, bytes]:
        from odoo.tools.safe_eval import safe_eval

        record = self._get(record_id)
        report = self.env.ref("account.account_invoices").with_user(1)
        filename = safe_eval(report.print_report_name, {"object": record})
        content = report._render([record.id], {"report_type": report.report_type})[0]
        return filename, content

from typing import Annotated

from fastapi import APIRouter, Depends

from odoo.api import Environment

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.fastapi.dependencies import authenticated_partner, odoo_env

from ..schemas import QuotationResponse, QuotationSearch

# create a router
quotation_router = APIRouter()


@quotation_router.get("/quotations/{quotation_id}")
def get(
    env: Annotated[Environment, Depends(odoo_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    quotation_id: str | None = None,
) -> QuotationResponse | None:
    quotation = env["sale.order"]._find_quotation(
        partner, quotation_id
    )  # récupérer la methode dans le abstrac que seb doit bientot migrer
    return quotation_id


@quotation_router.get("/quotations/confirm/{quotation_id}", status_code=200)
def confirm_quotation(
    env: Annotated[Environment, Depends(odoo_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    quotation_id: str | None = None,
) -> None:
    order = env["sale.order"]._get(quotation_id)
    env["sale.order"]._confirm(order)  # a confirmer


# le search est defini en get dans le module de base, faut il le passer en post
# pour beneficier du payload, plus facile pour passer des parama que l'URL parameter
@quotation_router.get("/quotations/search/{param}", status_code=200)
def search_quotation(
    env: Annotated[Environment, Depends(odoo_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    param: QuotationSearch | None = None,
) -> None:
    env["abstract.sale"]._paginate_search(**param)  # a verifier dans abstrac sale

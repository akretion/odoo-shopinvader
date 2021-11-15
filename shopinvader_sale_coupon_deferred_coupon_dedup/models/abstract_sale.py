from odoo.addons.component.core import AbstractComponent


class AbstractSaleService(AbstractComponent):
    _inherit = "shopinvader.abstract.sale.service"

    def _convert_one_sale(self, sale):
        res = super()._convert_one_sale(sale)
        res.update(
            {
                "applied_coupon_ids": self._convert_coupon(
                    sale.applied_coupon_ids + sale.unconfirmed_applied_coupon_ids
                ),
            }
        )
        return res

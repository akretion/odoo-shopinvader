# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_schema_sale.schemas import sale


class Sale(sale.Sale, extends=True):
    @classmethod
    def _get_futur_state(cls, odoo_rec):
        # V16 shopinvader_delivery_state
        if "delivery_state" in odoo_rec._fields:
            if odoo_rec.delivery_state == "partially":
                return "delivery_partial"
            elif odoo_rec.delivery_state == "done":
                return "delivery_done"
        # V16 shopinvader_api_quotation
        if odoo_rec.typology == "quotation" and odoo_rec.state == "draft":
            return "estimating"
        elif odoo_rec.typology == "quotation" and odoo_rec.state == "sent":
            return "estimated"
        # V16 shopinvader_sale_state
        elif odoo_rec.state == "cancel":
            return "cancel"
        elif odoo_rec.state == "done":
            return "delivery_full"
        elif odoo_rec.state in ("draft", "sent"):
            return "pending"
        else:
            return "processing"

    @classmethod
    def from_sale_order(cls, odoo_rec):
        res = super().from_sale_order(odoo_rec)
        res.state = cls._get_futur_state(odoo_rec)
        return res

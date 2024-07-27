# Copyright 2018 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models, fields, api



class ShopinvaderVariant(models.Model):
    _inherit = "shopinvader.variant"

    def _get_in_stock_states(self):
        return ["in_stock", "in_limited_stock"]

    sale_ok = fields.Boolean(compute="_compute_sale_ok")

    @api.depends("record_id", "record_id.sale_ok", "backend_id.default_sale_ok_policy", "sale_ok_policy", "stock_state")
    def _compute_sale_ok(self):
        for record in self:
            if not record.record_id.sale_ok:
                record.sale_ok = False
            else:
                policy = record.sale_ok_policy or record.backend_id.default_sale_ok_policy
                if policy == "refuse_order" and record.stock_state not in self._get_in_stock_states():
                    record.sale_ok = False
                else:
                    record.sale_ok = True

    sale_delay = fields.Char(compute="_compute_sale_delay")

    @api.depends("in_stock_delay", "out_of_stock_delay", "stock_state")
    def _compute_sale_delay(self):
        for record in self:
            if record.stock_state in self._get_in_stock_states():
                record.sale_delay = record.in_stock_delay
            else:
                record.sale_delay = record.out_of_stock_delay

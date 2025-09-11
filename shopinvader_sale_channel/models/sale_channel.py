# Copyright 2025 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class SaleChannel(models.Model):
    _inherit = "sale.channel"

    channel_type = fields.Selection(
        selection_add=[("shopinvader", "Shopinvader")],
    )

    @api.model
    def get_current(self):
        # TODO: PR in sale-channel
        # sale_channel = super().get_current()
        sale_channel = False
        if not sale_channel:
            sale_channel = self._get_current_fastapi_sale_channel()
        return sale_channel

    def _get_current_fastapi_sale_channel(self):
        fastapi_endpoint_id = self.env.context.get("fastapi_endpoint_id")
        if fastapi_endpoint_id:
            return (
                self.env["fastapi.endpoint"].browse(fastapi_endpoint_id).sale_channel_id
            )
        return None

from odoo import api, Command, fields, models

from odoo import _
from odoo.exceptions import UserError


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    shopinvader_backend_id = fields.Many2one(comodel_name="shopinvader.backend")

    def _params_from_fastapi_to_prepare_by_appending_id(self):
        return ["category", "team", "sale"]

    @api.model
    def _prepare_params_from_fastapi(self, params, mode="create"):
        if mode == "create":
            if params.get("partner"):
                partner = params.pop("partner")
                params["partner_name"] = partner.pop("name")
                params["partner_email"] = partner.pop("email")
                if "lang" in partner:
                    params["partner_lang"] = partner.pop("lang")

            elif self.env.context.get("authenticated_partner_id"):
                params["partner_id"] = self.env.context.get("authenticated_partner_id")
                params.pop("partner", None)
            else:
                raise UserError(_("The partner is mandatory"))

            # params["shopinvader_backend_id"] = self.shopinvader_backend.id
            # params["channel_id"] = self.shopinvader_backend.helpdesk_channel_id.id

        for key in self._params_from_fastapi_to_prepare_by_appending_id():
            val = params.pop(key)
            if val and "id" in val:
                params["%s_id" % key] = val["id"]
        return params

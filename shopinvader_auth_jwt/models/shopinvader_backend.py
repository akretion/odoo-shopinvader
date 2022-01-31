# Copyright 2021 ACSONE SA/NV (http://acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    jwt_aud = fields.Char(
        string="JWT audience",
        help="Use this backend when the JWT aud claim matches this.",
    )

    @api.model
    def _get_from_jwt_aud(self, aud):
        """On a record, ensure aud is valid
        on an empty recordset, will retrieve a record
        with aud"""
        if not aud:
            return self.browse([])
        if isinstance(aud, str):
            aud = [aud]
        if len(self.ids > 0):
            # self is a recordset
            if aud in self.jwt_aud:
                return self
            else:
                _logger.warning(
                    "Inconsistency between provided backend"
                    " and audience in jwt: "
                    f"Backend {self.name} ({self.jwt_aud} != {aud})"
                )
                return self.browse([])
        else:
            # self is an empty recordset
            backends = self.search([("jwt_aud", "in", aud)])
            if len(backends) != 1:
                _logger.warning(f"More than one backend found for JWT aud {aud}")
                return self.browse([])
            return backends

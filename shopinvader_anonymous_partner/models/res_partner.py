# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import secrets
import typing
from datetime import datetime

from odoo import _, api, fields, models

from odoo.addons.base.models.res_partner import Partner as ResPartner

COOKIE_NAME = "shopinvader-anonymous-partner"
COOKIE_MAX_AGE = 86400 * 365


class Response(typing.Protocol):
    def set_cookie(
        self,
        key: str,
        value: str,
        max_age: int,
        expires: datetime | str | int,
        secure: bool,
        httponly: bool,
        samesite: typing.Literal["lax", "strict", "none"],
    ) -> None:
        ...


class Cookies(typing.Protocol):
    def get(self, key: str) -> typing.Optional[str]:
        ...


class ResPartner(models.Model):
    _inherit = "res.partner"

    anonymous_token = fields.Char(
        help="Token used to uniquely and securely identify anonymous partners."
    )

    _sql_constraints = [
        (
            "anonymous_token_unique",
            "UNIQUE(anonymous_token)",
            "This token is already used!",
        )
    ]

    @api.model
    def _create_anonymous_partner__token(self):
        token = secrets.token_hex(32)
        return (
            self.env["res.partner"]
            .sudo()
            .create(
                {
                    "name": _("Anonymous (%s)") % (token[:8],),
                    "anonymous_token": token,
                    "active": False,
                }
            )
        )

    @api.model
    def _create_anonymous_partner__cookie(self, response: Response):
        partner = self._create_anonymous_partner__token()
        response.set_cookie(
            key=COOKIE_NAME,
            value=partner.anonymous_token,
            max_age=COOKIE_MAX_AGE,
            samesite="strict",
            secure=True,
            httponly=True,
        )
        return partner

    @api.model
    def _delete_anonymous_partner__cookie(self, cookies: Cookies, response: Response):
        """
        Delete anonymous partner and cookie
        """
        self._get_anonymous_partner__cookie(cookies).unlink()
        response.set_cookie(
            key=COOKIE_NAME,
            max_age=0,
            expires=0,
        )

    @api.model
    def _get_anonymous_partner__token(self, token: str):
        return (
            self.env["res.partner"]
            .sudo()
            .with_context(active_test=False)
            .search([("anonymous_token", "=", token)], limit=1)
        )

    @api.model
    def _get_anonymous_partner__cookie(self, cookies: Cookies):
        token = cookies.get(COOKIE_NAME)
        if not token:
            return self.env["res.partner"].sudo().browse()
        return self._get_anonymous_partner__token(token)

    def _promote_from_anonymous_partner(self, anonymous_partner: ResPartner):
        """
        Promote an anonymous partner to an authenticated partner.

        This method should be overridden by other modules to implement
        the partner resolution logic, merging the anonymous partner cart
        for instance.

        This method can return False to prevent the anonymous partner cookie
        from being deleted.
        """
        return True

    @api.model
    def _promote_anonymous_partner(
        self, partner: ResPartner, cookies: Cookies, response: Response
    ):
        """
        Promote the current anonymous partner to the given authenticated partner.

        This method calls the partner promotion and removes the anonymous partner cookie.
        """
        anonymous_partner = self._get_anonymous_partner__cookie(cookies)
        if partner._promote_from_anonymous_partner(
            anonymous_partner,
        ):
            self._delete_anonymous_partner__cookie(cookies, response)

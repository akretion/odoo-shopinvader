# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import contextlib
import time
from unittest.mock import Mock

import jwt

import odoo.http
from odoo.tools.misc import DotDict

from odoo.addons.shopinvader.tests.test_cart import CommonConnectedCartCase


class CommonTransferCartCase(CommonConnectedCartCase):
    @contextlib.contextmanager
    def _mock_request(self, authorization):
        environ = {}
        if authorization:
            environ["HTTP_AUTHORIZATION"] = authorization
        request = Mock(
            context={},
            db=self.env.cr.dbname,
            uid=None,
            httprequest=Mock(environ=environ, headers={}),
            session=DotDict(),
            env=self.env,
            cr=self.env.cr,
        )
        # These attributes are added upon successful auth, so make sure
        # calling hasattr on the mock when they are not yet set returns False.
        del request.jwt_payload
        del request.jwt_partner_id

        with contextlib.ExitStack() as s:
            odoo.http._request_stack.push(request)
            s.callback(odoo.http._request_stack.pop)
            yield request

    def _create_token(
        self,
        key="thesecret",
        audience="me",
        issuer="http://the.issuer",
        exp_delta=100,
        nbf=None,
        email=None,
    ):
        payload = dict(aud=audience, iss=issuer, exp=time.time() + exp_delta)
        if email:
            payload["email"] = email
        if nbf:
            payload["nbf"] = nbf
        return jwt.encode(payload, key=key, algorithm="HS256")

    def _create_validator(
        self,
        name,
        audience="me",
        issuer="http://the.issuer",
        secret_key="thesecret",
        partner_id_required=False,
        partner_id_strategy="email",
    ):
        return self.env["auth.jwt.validator"].create(
            dict(
                name=name,
                signature_type="secret",
                secret_algorithm="HS256",
                secret_key=secret_key,
                audience=audience,
                issuer=issuer,
                user_id_strategy="static",
                partner_id_strategy=partner_id_strategy,
                partner_id_required=partner_id_required,
            )
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_1 = cls.env.ref("product.product_product_4b")
        cls.product_2 = cls.env.ref("product.product_product_13")
        cls.product_3 = cls.env.ref("product.product_product_11")

    def setUp(self):
        super().setUp()

        with self.work_on_services(partner=self.partner) as work:
            self.service = work.component(usage="cart")

        self.guest = self.env.ref("shopinvader.partner_2")
        with self.work_on_services(partner=self.guest) as work:
            self.guest_service = work.component(usage="cart")

        self.guest_cart = self.env.ref("shopinvader.sale_order_3")
        self.token = self._create_token(email=self.partner.email)
        self.guest_token = self._create_token(email=self.guest.email)
        self._create_validator("shopinvader")

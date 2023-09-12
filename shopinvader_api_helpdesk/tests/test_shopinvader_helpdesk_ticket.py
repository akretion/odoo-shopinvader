# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json

from fastapi import status
from requests import Response

from odoo.tests.common import tagged

from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase

from ..routers import helpdesk_router


@tagged("post_install", "-at_install")
class TestShopinvaderHelpdeskApi(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.env["res.users"].create(
            {
                "name": "Test User",
                "login": "test_user",
                # "groups_id": [
                #     (
                #         6,
                #         0,
                #         [
                #             cls.env.ref(
                #                 "shopinvader_api_helpdesk.shopinvader_helpdesk_user_group"
                #             ).id
                #         ],
                #     )
                # ],
            }
        )

        cls.test_partner = cls.env["res.partner"].create(
            {
                "name": "FastAPI Shopinvader Helpdesk Demo",
                "street": "rue test",
                "zip": "1410",
                "city": "Waterloo",
                "country_id": cls.env.ref("base.be").id,
            }
        )

        cls.default_fastapi_authenticated_partner = cls.test_partner
        cls.default_fastapi_router = helpdesk_router

    def test_get_helpdesk_tickets(self):
        """
        Test to get helpdesk tickets of authenticated_partner
        """
        with self._create_test_client(router=helpdesk_router) as test_client:
            response: Response = test_client.get(
                "/helpdesk_ticket",
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )

        response_json = response.json()
        self.assertTrue(response_json)

        tickets = response_json
        self.assertTrue(tickets)
        self.assertGreaterEqual(len(tickets), 1)

    def test_get_helpdesk_ticket(self):
        """
        Test to get helpdesk tickets of authenticated_partner
        """
        with self._create_test_client(router=helpdesk_router) as test_client:
            response: Response = test_client.get(
                "/helpdesk_ticket/1",
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )

        response_json = response.json()
        self.assertTrue(response_json)

        ticket = response_json
        self.assertTrue(ticket)
        self.assertEqual(ticket["id"], 1)

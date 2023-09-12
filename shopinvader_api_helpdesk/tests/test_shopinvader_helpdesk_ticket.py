# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json

from fastapi import status
from requests import Response

from odoo.tests.common import tagged

from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase

from ..routers import helpdesk_router


@tagged("post_install", "-at_install")
class TestShopinvaderApiHelpdeskTicketCommon(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.default_fastapi_router = helpdesk_router

    def generate_ticket_data(self, partner=None):
        data = {
            "description": "My order is late",
            "name": "order num 4",
            "category": {"id": self.ref("helpdesk_mgmt.helpdesk_category_3")},
            "team": None,  # These should not be required but optional is ignored
            "sale": None,
        }
        if partner:
            data["partner"] = partner
        else:
            data["partner"] = None
        return data

    def assert_ticket_ok(self, ticket):
        self.assertEqual(len(ticket), 1)
        self.assertEqual(ticket.category_id.name, "Odoo")


# class TestShopinvaderApiHelpdeskTicketNoAccount(TestShopinvaderApiHelpdeskTicketCommon):
#     def test_create_helpdesk_ticket(self):
#         data = self.generate_ticket_data(
#             partner={
#                 "email": "customer+testststs@example.org",
#                 "name": "Customer",
#             }
#         )
#         with self._create_test_client(router=helpdesk_router) as test_client:
#             response: Response = test_client.post(
#                 "/helpdesk_ticket/create", content=json.dumps(data)
#             )

#             self.assertEqual(
#                 response.status_code,
#                 status.HTTP_201_CREATED,
#                 msg=f"error message: {response.text}",
#             )

#         ticket = self.env["helpdesk.ticket"].search(
#             [("partner_email", "=", "customer+testststs@example.org")]
#         )
#         self.assert_ticket_ok(ticket)

#     def test_create_ticket_noaccount_attachment(self):
#         data = self.generate_ticket_data(
#             partner={
#                 "email": "customer+testststs@example.org",
#                 "name": "Customer",
#             }
#         )
#         res = self.service.dispatch("create", content=json.dumps(data))
#         self.assertEqual(len(res["attachments"]), 0)
#         attachment_res = self.create_attachment(res["id"])
#         ticket = self.env["helpdesk.ticket"].search(
#             [("partner_email", "=", "customer+testststs@example.org")]
#         )
#         self.assert_ticket_ok(ticket)
#         self.assertEqual(ticket.attachment_ids.id, attachment_res["id"])
#         self.assertEqual(ticket.partner_id.email, ticket.partner_email)


class TestShopinvaderApiHelpdeskTicketConnected(TestShopinvaderApiHelpdeskTicketCommon):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.default_fastapi_authenticated_partner = cls.env.ref("base.res_partner_1")

    def test_get_helpdesk_tickets(self):
        """
        Test to get helpdesk tickets of authenticated_partner
        """
        with self._create_test_client(router=helpdesk_router) as test_client:
            response = test_client.get(
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

    def test_create_ticket_account_attachment(self):
        data = self.generate_ticket_data()

        with self._create_test_client(router=helpdesk_router) as test_client:
            response = test_client.post(
                "/helpdesk_ticket/create", content=json.dumps(data)
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                msg=f"error message: {response.text}",
            )

        response_json = response.json()
        # attachment_res = self.create_attachment(res["id"])
        ticket = self.env["helpdesk.ticket"].search([("id", "=", response_json["id"])])
        self.assert_ticket_ok(ticket)
        # self.assertEqual(ticket.attachment_ids.id, attachment_res["id"])

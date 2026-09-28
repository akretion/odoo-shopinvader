# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from fastapi import status
from requests import Response

from odoo.tests.common import tagged

from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase
from odoo.addons.shopinvader_schema_invoice.tests.common import InvoiceCaseMixin

from ..routers import invoice_router


@tagged("post_install", "-at_install")
class TestInvoice(FastAPITransactionCase, InvoiceCaseMixin):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls._setup_invoice_data()
        group = cls.env.ref(
            "shopinvader_api_security_invoice.shopinvader_accounting_user_group"
        )
        user = cls.env["res.users"].create(
            {
                "name": "Api User",
                "login": "user",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            group.id,
                        ],
                    )
                ],
            }
        )
        cls.default_fastapi_running_user = user
        cls.default_fastapi_authenticated_partner = cls.partner.with_user(user)
        cls.default_fastapi_router = invoice_router

        cls.other_partner = cls.env["res.partner"].create(
            {
                "name": "Other Test Partner",
                "email": "other@test.eu",
            }
        )

    def test_search_invoices_none(self):
        with self._create_test_client() as test_client:
            response: Response = test_client.get("/invoices")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 0)

    def test_search_invoices_not_ready(self):
        for __ in range(3):
            self._create_invoice(
                self.partner, self.product, account=self.account_receivable
            )
        with self._create_test_client() as test_client:
            response: Response = test_client.get("/invoices")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # still zero because state is not ok
        self.assertEqual(response.json()["count"], 0)

    def test_search_invoices_ok(self):
        for i in range(3):
            self._create_invoice(
                self.partner,
                self.product,
                account=self.account_receivable,
                validate=i != 2,
            )
        with self._create_test_client() as test_client:
            response: Response = test_client.get("/invoices")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 2 validated out of 3
        self.assertEqual(response.json()["count"], 2)

    def test_search_invoices_name(self):
        inv1 = self._create_invoice(
            self.partner,
            self.product,
            account=self.account_receivable,
            validate=True,
        )
        self._create_invoice(
            self.partner,
            self.product,
            account=self.account_receivable,
            validate=True,
        )
        with self._create_test_client() as test_client:
            response: Response = test_client.get(
                "/invoices", params={"name": inv1.name}
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["items"][0]["id"], inv1.id)

    def test_get_invoices(self):
        inv1 = self._create_invoice(
            self.partner,
            self.product,
            account=self.account_receivable,
            validate=True,
        )
        self._create_invoice(
            self.partner,
            self.product,
            account=self.account_receivable,
            validate=True,
        )
        with self._create_test_client() as test_client:
            response: Response = test_client.get(f"/invoices/{inv1.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], inv1.id)

    def test_get_invoices_wrong_partner(self):
        inv1 = self._create_invoice(
            self.other_partner,
            self.product,
            account=self.account_receivable,
            validate=True,
        )
        with self._create_test_client(raise_server_exceptions=False) as test_client:
            response: Response = test_client.get(f"/invoices/{inv1.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_download(self):
        inv1 = self._create_invoice(
            self.partner, self.product, account=self.account_receivable, validate=True
        )
        with self._create_test_client() as test_client:
            response: Response = test_client.get(f"/invoices/{inv1.id}/download")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "application/pdf")
        inv2 = self._create_invoice(
            self.partner, self.product, account=self.account_receivable, validate=True
        )
        with self._create_test_client() as test_client:
            response: Response = test_client.get(f"/invoices/{inv2.id}/download")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "application/pdf")

    def test_download_wrong_partner(self):
        inv1 = self._create_invoice(
            self.other_partner,
            self.product,
            account=self.account_receivable,
            validate=True,
        )

        with self._create_test_client(raise_server_exceptions=False) as test_client:
            response: Response = test_client.get(f"/invoices/{inv1.id}/download")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def _create_invoicing_address(self):
        """Return an invoicing address (a contact) of the authenticated partner."""
        return self.env["res.partner"].create(
            {
                "name": "Invoicing Address",
                "parent_id": self.partner.id,
                "type": "invoice",
            }
        )

    def test_search_invoices_on_invoicing_address(self):
        """An invoice done on an invoicing address of the partner is visible."""
        address = self._create_invoicing_address()
        address_invoice = self._create_invoice(
            address, self.product, account=self.account_receivable, validate=True
        )
        # an invoice of another partner must stay invisible
        self._create_invoice(
            self.other_partner,
            self.product,
            account=self.account_receivable,
            validate=True,
        )
        with self._create_test_client() as test_client:
            response: Response = test_client.get("/invoices")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["items"][0]["id"], address_invoice.id)

    def test_get_invoices_on_invoicing_address(self):
        """GET /invoices/{id} works for an invoice done on an address."""
        address = self._create_invoicing_address()
        address_invoice = self._create_invoice(
            address, self.product, account=self.account_receivable, validate=True
        )
        with self._create_test_client() as test_client:
            response: Response = test_client.get(f"/invoices/{address_invoice.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], address_invoice.id)

    def test_get_invoices_on_other_partner_address(self):
        """An invoice done on an address of another partner is not visible."""
        other_address = self.env["res.partner"].create(
            {
                "name": "Other Invoicing Address",
                "parent_id": self.other_partner.id,
                "type": "invoice",
            }
        )
        other_invoice = self._create_invoice(
            other_address, self.product, account=self.account_receivable, validate=True
        )
        with self._create_test_client(raise_server_exceptions=False) as test_client:
            response: Response = test_client.get(f"/invoices/{other_invoice.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

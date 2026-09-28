# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from fastapi import status
from requests import Response

from odoo.exceptions import UserError
from odoo.tests.common import tagged

from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase

from ..routers import address_router


@tagged("post_install", "-at_install")
class TestShopinvaderAddressApi(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.env["res.users"].create(
            {
                "name": "Test User",
                "login": "test_user",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref(
                                "shopinvader_api_address.shopinvader_address_user_group"
                            ).id
                        ],
                    )
                ],
            }
        )

        cls.test_partner = cls.env["res.partner"].create(
            {
                "name": "FastAPI Shopinvader Address Demo",
                "street": "rue test",
                "zip": "1410",
                "city": "Waterloo",
                "country_id": cls.env.ref("base.be").id,
                "title": cls.env.ref("base.res_partner_title_madam").id,
            }
        )

        cls.default_fastapi_authenticated_partner = cls.test_partner
        cls.default_fastapi_router = address_router

    def test_get_invoicing_address(self):
        """
        Test to get address of authenticated_partner
        """
        with self._create_test_client(router=address_router) as test_client:
            response: Response = test_client.get(
                "/addresses/invoicing",
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )

        response_json = response.json()
        self.assertTrue(response_json)

        address = response_json[0]

        self.assertEqual(address.get("name"), self.test_partner.name)
        self.assertEqual(address.get("street"), self.test_partner.street)
        self.assertEqual(address.get("zip"), self.test_partner.zip)
        self.assertEqual(address.get("city"), self.test_partner.city)
        self.assertEqual(address.get("country_id"), self.test_partner.country_id.id)
        self.assertEqual(address.get("id"), self.test_partner.id)
        self.assertEqual(address.get("title_id"), self.test_partner.title.id)

        with self._create_test_client(router=address_router) as test_client:
            response: Response = test_client.get(
                f"/addresses/invoicing/{self.test_partner.id}",
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )

        response_json = response.json()
        self.assertTrue(response_json)

        address = response_json

        self.assertEqual(address.get("name"), self.test_partner.name)
        self.assertEqual(address.get("street"), self.test_partner.street)
        self.assertEqual(address.get("zip"), self.test_partner.zip)
        self.assertEqual(address.get("city"), self.test_partner.city)
        self.assertEqual(address.get("country_id"), self.test_partner.country_id.id)
        self.assertEqual(address.get("id"), self.test_partner.id)
        self.assertEqual(address.get("title_id"), self.test_partner.title.id)

    def test_get_delivery_address(self):
        """
        Test to get delivery address of authenticated_partner
        """

        with self._create_test_client(router=address_router) as test_client:
            response: Response = test_client.get(
                "/addresses/delivery",
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )

        response_json = response.json()
        self.assertEqual(0, len(response_json))

        # add delivery address
        new_address = self.env["res.partner"].create(
            {
                "name": "test New Addr",
                "street": "test Street",
                "zip": "5000",
                "city": "Namur",
                "country_id": self.env.ref("base.be").id,
                "parent_id": self.test_partner.id,
                "type": "delivery",
            }
        )

        with self._create_test_client(router=address_router) as test_client:
            response: Response = test_client.get(
                "/addresses/delivery",
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )

        response_json = response.json()
        self.assertTrue(response_json)

        address = response_json[0]

        self.assertEqual(address.get("name"), new_address.name)
        self.assertEqual(address.get("street"), new_address.street)
        self.assertEqual(address.get("zip"), new_address.zip)
        self.assertEqual(address.get("city"), new_address.city)
        self.assertEqual(address.get("country_id"), new_address.country_id.id)
        self.assertEqual(address.get("id"), new_address.id)

        with self._create_test_client(router=address_router) as test_client:
            response: Response = test_client.get(
                f"/addresses/delivery/{new_address.id}",
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )

        response_json = response.json()

        address = response_json

        self.assertEqual(address.get("name"), new_address.name)
        self.assertEqual(address.get("street"), new_address.street)
        self.assertEqual(address.get("zip"), new_address.zip)
        self.assertEqual(address.get("city"), new_address.city)
        self.assertEqual(address.get("country_id"), new_address.country_id.id)
        self.assertEqual(address.get("id"), new_address.id)

    def test_update_invoicing_address(self):
        """
        Test to update invoicing address
        """
        data = {
            "name": "FastAPI Shopinvader Address Demo",
            "zip": "1410",
            "city": "Waterloo",
            "country_id": self.env.ref("base.be").id,
            "street": "test Street",
            "title_id": self.env.ref("base.res_partner_title_madam").id,
        }

        with self._create_test_client(router=address_router) as test_client:
            response: Response = test_client.post(
                f"/addresses/invoicing/{self.test_partner.id}", json=data
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )
        response_json = response.json()
        self.assertTrue(response_json)

        address = response_json

        self.assertEqual(address.get("street"), "test Street")
        self.assertEqual(address.get("street"), self.test_partner.street)

    def test_update_invoicing_address_vat(self):
        """
        Test to update invoicing address vat
        """
        data = {
            "name": "FastAPI Shopinvader Address Demo",
            "zip": "1410",
            "city": "Waterloo",
            "country_id": self.env.ref("base.be").id,
            "street": "rue test",
            "vat": "BE0477472701",
        }

        with self._create_test_client(router=address_router) as test_client:
            response: Response = test_client.post(
                f"/addresses/invoicing/{self.test_partner.id}", json=data
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )
        response_json = response.json()
        self.assertTrue(response_json)

        address = response_json

        self.assertEqual(address.get("vat"), "BE0477472701")
        self.assertEqual(address.get("vat"), self.test_partner.vat)

    def test_get_address_vat(self):
        """
        The vat of every address is the vat of the customer account
        """
        self.test_partner.vat = "BE0477472701"
        contact = self.env["res.partner"].create(
            {
                "name": "Service comptabilite",
                "parent_id": self.test_partner.id,
                "type": "invoice",
            }
        )
        delivery_address = self.env["res.partner"].create(
            {
                "name": "Depot",
                "parent_id": self.test_partner.id,
                "type": "delivery",
            }
        )

        with self._create_test_client(router=address_router) as test_client:
            invoicing_response: Response = test_client.get("/addresses/invoicing")
            delivery_response: Response = test_client.get("/addresses/delivery")

        self.assertEqual(
            invoicing_response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {invoicing_response.text}",
        )
        self.assertEqual(
            delivery_response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {delivery_response.text}",
        )

        addresses = {
            address["id"]: address
            for address in (invoicing_response.json() + delivery_response.json())
        }
        self.assertEqual(
            set(addresses), {self.test_partner.id, contact.id, delivery_address.id}
        )
        for address in addresses.values():
            # the vat is a commercial field of the account: it is the same for
            # all the addresses of the account
            self.assertEqual(address["vat"], "BE0477472701")
            self.assertFalse(address["vat_readonly"])

    def test_get_address_vat_readonly(self):
        """
        The vat is readonly as soon as the account has a confirmed sale order
        """
        self.test_partner.vat = "BE0477472701"
        delivery_address = self.env["res.partner"].create(
            {
                "name": "Depot",
                "parent_id": self.test_partner.id,
                "type": "delivery",
            }
        )
        order = self.env["sale.order"].create({"partner_id": self.test_partner.id})

        with self._create_test_client(router=address_router) as test_client:
            response: Response = test_client.get(
                f"/addresses/invoicing/{self.test_partner.id}"
            )
            delivery_response: Response = test_client.get(
                f"/addresses/delivery/{delivery_address.id}"
            )

        # a draft sale order (cart, quotation) does not freeze the vat
        self.assertFalse(response.json()["vat_readonly"])
        self.assertFalse(delivery_response.json()["vat_readonly"])

        order.write({"state": "sale"})

        with self._create_test_client(router=address_router) as test_client:
            response: Response = test_client.get(
                f"/addresses/invoicing/{self.test_partner.id}"
            )
            delivery_response: Response = test_client.get(
                f"/addresses/delivery/{delivery_address.id}"
            )

        for address in (response.json(), delivery_response.json()):
            self.assertEqual(address["vat"], "BE0477472701")
            self.assertTrue(address["vat_readonly"])

    def test_create_delivery_address(self):
        """
        Test to create delivery address
        """
        data = {
            "name": "test Addr",
            "street": "test Street",
            "zip": "5000",
            "city": "Namur",
            "country_id": self.env.ref("base.be").id,
        }

        with self._create_test_client(router=address_router) as test_client:
            response: Response = test_client.post("/addresses/delivery", json=data)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            msg=f"error message: {response.text}",
        )
        response_json = response.json()
        self.assertTrue(response_json)

        address = response_json

        self.assertEqual(address.get("street"), "test Street")
        self.assertNotEqual(address.get("street"), self.test_partner.street)

        address_odoo = self.env["res.partner"].browse(address.get("id"))
        self.assertEqual(address_odoo.type, "delivery")

    def test_delete_delivery_address(self):
        """
        Test to delete delivery address
        """

        new_address = self.env["res.partner"].create(
            {
                "name": "test New Addr",
                "street": "test Street",
                "zip": "5000",
                "city": "Namur",
                "country_id": self.env.ref("base.be").id,
                "parent_id": self.test_partner.id,
                "type": "delivery",
            }
        )

        with self._create_test_client(router=address_router) as test_client:
            response: Response = test_client.delete(
                f"/addresses/delivery/{new_address.id}",
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )
        self.assertFalse(new_address.active)

    def test_update_delivery_address(self):
        """
        Test to update delivery address
        """
        new_address = self.env["res.partner"].create(
            {
                "name": "test New Addr",
                "street": "test Street",
                "zip": "5000",
                "city": "Namur",
                "country_id": self.env.ref("base.be").id,
                "parent_id": self.test_partner.id,
                "type": "delivery",
            }
        )

        data = {
            "name": "test Addr2",
            "street": "test Street2",
            "zip": "5000",
            "city": "Namur",
            "country_id": self.env.ref("base.be").id,
        }

        with self._create_test_client(router=address_router) as test_client:
            response: Response = test_client.post(
                f"/addresses/delivery/{new_address.id}", json=data
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )
        self.assertEqual(new_address.name, data.get("name"))
        self.assertEqual(new_address.street, data.get("street"))


@tagged("post_install", "-at_install")
class TestShopinvaderAddressReplacementApi(FastAPITransactionCase):
    """Shopinvader address API: an address used on a confirmed sale order is
    never updated (nor deleted), it is replaced by a new one."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.customer = cls.env["res.partner"].create(
            {
                "name": "Shopinvader Address Replacement Demo",
                "street": "Rue du test",
                "zip": "1410",
                "city": "Waterloo",
                "country_id": cls.env.ref("base.be").id,
            }
        )
        cls.default_fastapi_authenticated_partner = cls.customer
        cls.default_fastapi_router = address_router

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _create_address(self, address_type, **vals):
        vals.setdefault("name", "Contact")
        vals.setdefault("street", "Rue du contact")
        vals.setdefault("country_id", self.env.ref("base.be").id)
        return self.env["res.partner"].create(
            dict(vals, parent_id=self.customer.id, type=address_type)
        )

    def _use_address_on_sale_order(self, address_type, address):
        """Put the address on a confirmed sale order.

        Only the state of the sale order matters for the checks under test, so
        the order is not really validated (no line, no tax computation).
        """
        field_name = (
            "partner_invoice_id"
            if address_type == "invoicing"
            else "partner_shipping_id"
        )
        order = self.env["sale.order"].create({"partner_id": self.customer.id})
        order.write({field_name: address.id})
        order.write({"state": "sale"})
        return order

    def _create_open_order(self, address_type, address):
        """Create a draft sale order (cart/quotation) using the address."""
        field_name = (
            "partner_invoice_id"
            if address_type == "invoicing"
            else "partner_shipping_id"
        )
        order = self.env["sale.order"].create({"partner_id": self.customer.id})
        order.write({field_name: address.id})
        return order

    def _get(self, path) -> Response:
        with self._create_test_client(
            router=address_router, raise_server_exceptions=False
        ) as test_client:
            return test_client.get(path)

    def _post(self, path, data=None) -> Response:
        with self._create_test_client(
            router=address_router, raise_server_exceptions=False
        ) as test_client:
            return test_client.post(path, json=data)

    def _delete(self, path) -> Response:
        with self._create_test_client(
            router=address_router, raise_server_exceptions=False
        ) as test_client:
            return test_client.delete(path)

    def _address_ids(self, address_type) -> list:
        response = self._get(f"/addresses/{address_type}")
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )
        return [address["id"] for address in response.json()]

    # ------------------------------------------------------------------
    # Delivery addresses
    # ------------------------------------------------------------------
    def test_update_delivery_address_not_used(self):
        """An address not used on a confirmed sale order is updated in place."""
        address = self._create_address("delivery")
        data = {"name": "Contact", "street": "Nouvelle rue", "zip": "5000"}

        response = self._post(f"/addresses/delivery/{address.id}", data)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )
        self.assertEqual(response.json()["id"], address.id)
        self.assertEqual(address.street, "Nouvelle rue")
        self.assertTrue(address.active)
        self.assertFalse(address.shopinvader_address_disabled)
        self.assertEqual(self._address_ids("delivery"), [address.id])

    def test_update_delivery_address_used(self):
        """An address used on a confirmed sale order is replaced by a new one."""
        address = self._create_address("delivery", street="Ancienne rue")
        order = self._use_address_on_sale_order("delivery", address)
        cart = self._create_open_order("delivery", address)
        data = {"name": "Contact", "street": "Nouvelle rue", "zip": "5000"}

        response = self._post(f"/addresses/delivery/{address.id}", data)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )
        new_address = self.env["res.partner"].browse(response.json()["id"])
        # a new address is created with the given values
        self.assertNotEqual(new_address, address)
        self.assertEqual(new_address.street, "Nouvelle rue")
        self.assertEqual(new_address.zip, "5000")
        self.assertEqual(new_address.type, "delivery")
        self.assertEqual(new_address.parent_id, self.customer)
        self.assertTrue(new_address.active)
        # the replaced address is kept for the history
        self.assertFalse(address.active)
        self.assertEqual(order.partner_shipping_id, address)
        # the open documents follow the replacement
        self.assertEqual(cart.partner_shipping_id, new_address)
        # only the new address is exposed by the API
        self.assertEqual(self._address_ids("delivery"), [new_address.id])

    def test_update_delivery_address_main_partner_used(self):
        """The address to update is the partner itself: it is flagged and a
        delivery contact takes its place."""
        order = self._use_address_on_sale_order("delivery", self.customer)
        cart = self._create_open_order("delivery", self.customer)
        data = {"name": "Shopinvader Address Replacement Demo", "street": "Rue 2"}

        response = self._post(f"/addresses/delivery/{self.customer.id}", data)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )
        new_address = self.env["res.partner"].browse(response.json()["id"])
        self.assertEqual(new_address.street, "Rue 2")
        self.assertEqual(new_address.type, "delivery")
        # the customer account is flagged: it is not an address anymore
        self.assertTrue(self.customer.shopinvader_address_disabled)
        self.assertTrue(self.customer.active)
        self.assertEqual(self.customer.street, "Rue du test")
        self.assertEqual(order.partner_shipping_id, self.customer)
        self.assertEqual(cart.partner_shipping_id, new_address)
        self.assertEqual(self._address_ids("delivery"), [new_address.id])
        self.assertEqual(
            self._get(f"/addresses/delivery/{self.customer.id}").status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_delete_delivery_address_not_used(self):
        """An address not used on a confirmed sale order is archived."""
        address = self._create_address("delivery")

        response = self._delete(f"/addresses/delivery/{address.id}")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )
        self.assertFalse(address.active)
        self.assertEqual(self._address_ids("delivery"), [])

    def test_delete_delivery_address_used(self):
        """An address used on a confirmed sale order is archived instead of
        being refused, and the open documents fall back on the default."""
        address = self._create_address("delivery")
        order = self._use_address_on_sale_order("delivery", address)
        cart = self._create_open_order("delivery", address)

        response = self._delete(f"/addresses/delivery/{address.id}")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )
        self.assertFalse(address.active)
        self.assertEqual(order.partner_shipping_id, address)
        self.assertEqual(cart.partner_shipping_id, self.customer)
        self.assertEqual(self._address_ids("delivery"), [])

    def test_delete_delivery_address_linked_to_user(self):
        """An address that cannot be archived (linked to a user) is flagged."""
        address = self._create_address("delivery")
        self.env["res.users"].create(
            {
                "name": "Shopinvader Address Demo User",
                "login": "shopinvader_address_demo_user",
                "partner_id": address.id,
            }
        )

        response = self._delete(f"/addresses/delivery/{address.id}")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )
        self.assertTrue(address.active)
        self.assertTrue(address.shopinvader_address_disabled)
        self.assertEqual(self._address_ids("delivery"), [])

    # ------------------------------------------------------------------
    # Invoicing addresses
    # ------------------------------------------------------------------
    def test_create_invoicing_address(self):
        """A new invoicing address can be created as a contact of the account."""
        data = {
            "name": "Service comptabilite",
            "street": "Rue de la facturation",
            "zip": "1000",
            "city": "Bruxelles",
            "country_id": self.env.ref("base.be").id,
            "vat": "BE0477472701",
        }

        response = self._post("/addresses/invoicing", data)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            msg=f"error message: {response.text}",
        )
        new_address = self.env["res.partner"].browse(response.json()["id"])
        self.assertEqual(new_address.street, "Rue de la facturation")
        self.assertEqual(new_address.type, "invoice")
        self.assertEqual(new_address.parent_id, self.customer)
        # the vat of an invoicing address belongs to the customer account
        self.assertEqual(self.customer.vat, "BE0477472701")
        self.assertEqual(new_address.vat, "BE0477472701")
        # the customer account is still an invoicing address of the API
        self.assertEqual(
            self._address_ids("invoicing"), [self.customer.id, new_address.id]
        )

    def test_update_invoicing_address_not_used(self):
        """An invoicing address not used on a confirmed sale order is updated
        in place, even if it is the partner itself."""
        data = {"name": self.customer.name, "street": "Nouvelle rue"}

        response = self._post(f"/addresses/invoicing/{self.customer.id}", data)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )
        self.assertEqual(response.json()["id"], self.customer.id)
        self.assertEqual(self.customer.street, "Nouvelle rue")
        self.assertFalse(self.customer.shopinvader_address_disabled)

    def test_update_invoicing_address_main_partner_used(self):
        """The invoicing address of the account is used: it is flagged, the new
        address takes its place and the vat of the account follows."""
        order = self._use_address_on_sale_order("invoicing", self.customer)
        cart = self._create_open_order("invoicing", self.customer)
        data = {
            "name": self.customer.name,
            "street": "Nouvelle rue",
            "zip": "1000",
            "country_id": self.env.ref("base.be").id,
            "vat": "BE0477472701",
        }

        response = self._post(f"/addresses/invoicing/{self.customer.id}", data)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )
        new_address = self.env["res.partner"].browse(response.json()["id"])
        self.assertNotEqual(new_address, self.customer)
        self.assertEqual(new_address.type, "invoice")
        self.assertEqual(new_address.street, "Nouvelle rue")
        self.assertEqual(new_address.vat, "BE0477472701")
        # the account is kept as is (its data is used by the old documents) but
        # the fiscal position of the new orders needs to be up to date
        self.assertEqual(self.customer.street, "Rue du test")
        self.assertEqual(self.customer.vat, "BE0477472701")
        self.assertTrue(self.customer.shopinvader_address_disabled)
        self.assertEqual(order.partner_invoice_id, self.customer)
        self.assertEqual(cart.partner_invoice_id, new_address)
        # the API only exposes the new invoicing address
        self.assertEqual(self._address_ids("invoicing"), [new_address.id])
        self.assertEqual(
            self._get(f"/addresses/invoicing/{self.customer.id}").status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_update_invoicing_address_contact_used(self):
        """An invoicing contact used on a confirmed sale order is archived and
        replaced by a new contact."""
        # the vat is a commercial field: it always belongs to the customer
        # account and is synchronized on its contacts by Odoo
        self.customer.vat = "BE0477472701"
        address = self._create_address("invoice")
        self.assertEqual(address.vat, "BE0477472701")
        order = self._use_address_on_sale_order("invoicing", address)
        data = {"name": "Contact", "street": "Nouvelle rue"}

        response = self._post(f"/addresses/invoicing/{address.id}", data)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )
        new_address = self.env["res.partner"].browse(response.json()["id"])
        self.assertNotEqual(new_address, address)
        self.assertEqual(new_address.type, "invoice")
        self.assertEqual(new_address.street, "Nouvelle rue")
        # the replaced address is archived, the vat follows the account
        self.assertFalse(address.active)
        self.assertEqual(new_address.vat, "BE0477472701")
        self.assertEqual(order.partner_invoice_id, address)
        self.assertEqual(
            self._address_ids("invoicing"), [self.customer.id, new_address.id]
        )

    def test_delete_invoicing_address_contact(self):
        """An invoicing contact can be archived, the account itself cannot."""
        address = self._create_address("invoice")
        self.customer._delete_shopinvader_invoicing_address(address)
        self.assertFalse(address.active)

        with self.assertRaises(UserError):
            self.customer._delete_shopinvader_invoicing_address(self.customer)

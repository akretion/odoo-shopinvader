# Copyright 2026 Akretion (http://www.akretion.com).
# @author Benoît Guillot <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import mock

from fastapi import status
from requests import Response

from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase
from odoo.addons.shopinvader_api_address.routers import address_router
from odoo.addons.shopinvader_api_settings.routers import settings_router


class TestShopinvaderAddressEinvoicingCommon(FastAPITransactionCase):
    """A customer account with its French eInvoicing directory."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.env["res.users"].create(
            {
                "name": "Test User",
                "login": "test_user_einvoicing",
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
        cls.customer = cls.env["res.partner"].create(
            {
                "name": "FastAPI Shopinvader eInvoicing Demo",
                "is_company": True,
                "street": "rue test",
                "zip": "1410",
                "city": "Waterloo",
                "country_id": cls.env.ref("base.fr").id,
            }
        )
        cls.default_fastapi_authenticated_partner = cls.customer
        cls.default_fastapi_router = address_router

        # the directory lines always belong to the commercial entity of the
        # account (domain parent_id = False on fr.directory.line)
        directory_line = cls.env["fr.directory.line"].sudo()
        cls.siren_line = directory_line.create(
            {
                "partner_id": cls.customer.id,
                "identifier": "732829320",
                "type": "siren",
                "state": "active",
            }
        )
        cls.routing_code_line = directory_line.create(
            {
                "partner_id": cls.customer.id,
                "identifier": "0009",
                "type": "routing_code",
                "state": "active",
                "routing_code_name": "ROUTAGE",
            }
        )
        cls.disabled_line = directory_line.create(
            {
                "partner_id": cls.customer.id,
                "identifier": "111111111",
                "type": "siren",
                "state": "disabled",
            }
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _call(
        self, url, http_code=status.HTTP_200_OK, router=None, partner=None, **kwargs
    ):
        method = kwargs.pop("method", "get")
        with self._create_test_client(
            router=router or self.default_fastapi_router,
            partner=partner,
            raise_server_exceptions=False,
        ) as test_client:
            response: Response = getattr(test_client, method)(url, **kwargs)
        self.assertEqual(
            response.status_code, http_code, msg=f"error message: {response.text}"
        )
        return response.json()

    def _directory_line_payload(self, directory_line):
        return {
            "id": directory_line.id,
            "identifier": directory_line.identifier,
            "type": directory_line.type,
            "state": directory_line.state,
            "routing_code_name": directory_line.routing_code_name or None,
        }

    def _create_address(self, address_type, **vals):
        vals.setdefault("name", "Contact")
        vals.setdefault("country_id", self.env.ref("base.fr").id)
        return self.env["res.partner"].create(
            dict(vals, parent_id=self.customer.id, type=address_type)
        )


class TestShopinvaderAddressEinvoicingApi(TestShopinvaderAddressEinvoicingCommon):
    """The addresses exposed by the API expose the eInvoicing directory."""

    def test_get_addresses_directory_lines(self):
        """Every address of the account exposes the same directory lines."""
        delivery_address = self._create_address("delivery")
        addresses = self._call("/addresses/invoicing") + self._call(
            "/addresses/delivery"
        )

        self.assertEqual(
            sorted(address["id"] for address in addresses),
            sorted([self.customer.id, delivery_address.id]),
        )
        for address in addresses:
            # the disabled line is hidden by the One2many, as in Odoo
            self.assertEqual(
                address["fr_directory_line_ids"],
                [
                    self._directory_line_payload(self.routing_code_line),
                    self._directory_line_payload(self.siren_line),
                ],
            )
            self.assertIsNone(address["default_fr_directory_line_id"])

    def test_get_address_default_directory_line(self):
        """The line of the address wins, the one of the account is a fallback."""
        self.customer.default_fr_directory_line_id = self.siren_line
        contact = self._create_address("invoice")

        # a contact without its own line exposes the line of the account
        address = self._call(f"/addresses/invoicing/{contact.id}")
        self.assertEqual(
            address["default_fr_directory_line_id"],
            self._directory_line_payload(self.siren_line),
        )
        # the line of the contact itself wins
        contact.default_fr_directory_line_id = self.routing_code_line
        address = self._call(f"/addresses/invoicing/{contact.id}")
        self.assertEqual(
            address["default_fr_directory_line_id"],
            self._directory_line_payload(self.routing_code_line),
        )
        # the account exposes its own line
        address = self._call(f"/addresses/invoicing/{self.customer.id}")
        self.assertEqual(
            address["default_fr_directory_line_id"],
            self._directory_line_payload(self.siren_line),
        )

    def test_update_address_default_directory_line(self):
        """The default line can be set and removed from the front end."""
        delivery_address = self._create_address("delivery")

        address = self._call(
            f"/addresses/delivery/{delivery_address.id}",
            method="post",
            json={"default_fr_directory_line_id": self.siren_line.id},
        )
        self.assertEqual(
            address["default_fr_directory_line_id"],
            self._directory_line_payload(self.siren_line),
        )
        self.assertEqual(delivery_address.default_fr_directory_line_id, self.siren_line)

        # an explicit null removes the selected line
        address = self._call(
            f"/addresses/delivery/{delivery_address.id}",
            method="post",
            json={"default_fr_directory_line_id": None},
        )
        self.assertIsNone(address["default_fr_directory_line_id"])
        self.assertFalse(delivery_address.default_fr_directory_line_id)

        # the invoicing address (the account itself) can be updated as well
        self._call(
            f"/addresses/invoicing/{self.customer.id}",
            method="post",
            json={"default_fr_directory_line_id": self.routing_code_line.id},
        )
        self.assertEqual(
            self.customer.default_fr_directory_line_id, self.routing_code_line
        )


class TestShopinvaderAddressEinvoicingDirectorySync(
    TestShopinvaderAddressEinvoicingCommon
):
    """The customer can sync its directory from the site."""

    def test_sync_directory_lines(self):
        """The vat is stored on the account and the directory lines returned."""
        synced_partners = []

        def fake_sync_button(partner):
            """Fake the query of the French directory (no CTC session in tests)."""
            synced_partners.append(partner)
            partner.env["fr.directory.line"].sudo().create(
                {
                    "partner_id": partner.id,
                    "identifier": "123456789",
                    "type": "siret",
                    "state": "active",
                }
            )

        with mock.patch.object(
            type(self.env["res.partner"]), "fr_directory_sync_button", fake_sync_button
        ):
            directory_lines = self._call(
                "/einvoicing/directory_lines",
                method="post",
                json={"vat": "FR 44 732829320"},
            )

        # the directory is always synced on the main partner (the account)
        self.assertEqual(synced_partners, [self.customer])
        # the vat received from the customer has been written on the account
        self.assertEqual(self.customer.vat, "FR44732829320")
        self.assertEqual(
            [directory_line["identifier"] for directory_line in directory_lines],
            ["0009", "123456789", "732829320"],
        )
        self.assertEqual(directory_lines[1]["type"], "siret")
        self.assertEqual(directory_lines[1]["state"], "active")

    def test_sync_directory_lines_without_vat(self):
        """The directory can be synced without sending a vat number."""
        self.customer.vat = "FR44732829320"
        synced_partners = []

        def fake_sync_button(partner):
            synced_partners.append(partner)

        with mock.patch.object(
            type(self.env["res.partner"]), "fr_directory_sync_button", fake_sync_button
        ):
            directory_lines = self._call(
                "/einvoicing/directory_lines",
                method="post",
                json={},
            )

        self.assertEqual(synced_partners, [self.customer])
        # the vat of the account is left untouched
        self.assertEqual(self.customer.vat, "FR44732829320")
        self.assertEqual(
            [directory_line["identifier"] for directory_line in directory_lines],
            ["0009", "732829320"],
        )

    def test_sync_directory_lines_from_a_contact(self):
        """The directory is always synced on the commercial entity.

        The authenticated partner can be a contact of the account: the vat is
        written on the account and the directory is queried with the data of
        the account.
        """
        contact = self._create_address("invoice")
        synced_partners = []

        def fake_sync_button(partner):
            """Fake the query of the French directory (no CTC session in tests)."""
            synced_partners.append(partner)

        with mock.patch.object(
            type(self.env["res.partner"]), "fr_directory_sync_button", fake_sync_button
        ):
            directory_lines = self._call(
                "/einvoicing/directory_lines",
                method="post",
                json={"vat": "FR44732829320"},
                partner=contact,
            )

        self.assertEqual(synced_partners, [self.customer])
        self.assertEqual(self.customer.vat, "FR44732829320")
        self.assertEqual(
            [directory_line["identifier"] for directory_line in directory_lines],
            ["0009", "732829320"],
        )


class TestShopinvaderAddressEinvoicingCountry(TestShopinvaderAddressEinvoicingCommon):
    """The settings expose the countries on which eInvoicing applies."""

    def test_settings_countries_einvoicing(self):
        settings = self._call("/settings", router=settings_router)
        countries = {country["code"]: country for country in settings["countries"]}

        self.assertTrue(countries["FR"]["einvoicing"])
        self.assertFalse(countries["BE"]["einvoicing"])

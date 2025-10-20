# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestAddressInvoicingEdition(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_partner = cls.env["res.partner"].create(
            {
                "name": "Shopinvader Address Demo",
                "street": "rue du test",
                "zip": "18450",
                "city": "Vailly-sur-Sauldre",
                "country_id": cls.env.ref("base.fr").id,
                "title": cls.env.ref("base.res_partner_title_madam").id,
            }
        )

        cls.test_partner_invoicing_address = cls.env["res.partner"].create(
            {
                "name": "Invoicing Address",
                "street": "rue de la facturation",
                "zip": "75001",
                "city": "Paris",
                "country_id": cls.env.ref("base.fr").id,
                "type": "invoice",
                "parent_id": cls.test_partner.id,
            }
        )

    def test_get_shopinvader_invoicing_addresses(self):
        invoicing_address = self.test_partner._get_shopinvader_invoicing_addresses()
        self.assertEqual(
            invoicing_address,
            self.test_partner_invoicing_address,
            "The invoicing address returned is not the expected one",
        )

    def test_get_shopinvader_invoicing_addresses_with_no_invoice_address(self):
        self.test_partner_invoicing_address.unlink()
        invoicing_address = self.test_partner._get_shopinvader_invoicing_addresses()
        self.assertEqual(
            invoicing_address,
            self.test_partner,
            "The invoicing address returned is not the expected one",
        )

    def test_update_shopinvader_invoicing_address_no_create(self):
        vals = {
            "street": "rue modifiée",
            "city": "Ville modifiée",
        }
        updated_address = self.test_partner._update_shopinvader_invoicing_address(
            vals, self.test_partner_invoicing_address
        )
        self.assertEqual(
            updated_address,
            self.test_partner_invoicing_address,
            "The invoicing address should have been updated in place",
        )
        self.assertEqual(updated_address.street, "rue modifiée")
        self.assertEqual(updated_address.city, "Ville modifiée")
        self.assertNotEqual(self.test_partner.street, "rue modifiée")
        self.assertNotEqual(self.test_partner.city, "Ville modifiée")

    def test_update_shopinvader_invoicing_address_create_as_used(self):
        vals = {
            "street": "rue modifiée",
            "city": "Ville modifiée",
        }
        # Simulate that the main partner has sales orders with this invoicing address
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.test_partner.id,
                "partner_invoice_id": self.test_partner_invoicing_address.id,
            }
        )
        sale_order.action_confirm()
        updated_address = self.test_partner._update_shopinvader_invoicing_address(
            vals, self.test_partner_invoicing_address
        )
        self.assertNotEqual(
            updated_address,
            self.test_partner_invoicing_address,
            "A new invoicing address should have been created",
        )
        self.assertEqual(updated_address.street, "rue modifiée")
        self.assertEqual(updated_address.city, "Ville modifiée")
        self.assertEqual(updated_address.parent_id, self.test_partner)
        self.assertEqual(updated_address.type, "invoice")
        self.assertNotEqual(self.test_partner_invoicing_address.street, "rue modifiée")
        self.assertNotEqual(self.test_partner_invoicing_address.city, "Ville modifiée")
        self.assertNotEqual(self.test_partner.street, "rue modifiée")
        self.assertNotEqual(self.test_partner.city, "Ville modifiée")

    def test_update_shopinvader_invoicing_address_create_as_none(self):
        self.test_partner_invoicing_address.unlink()
        vals = {
            "street": "rue modifiée",
            "city": "Ville modifiée",
        }
        updated_address = self.test_partner._update_shopinvader_invoicing_address(
            vals, self.test_partner
        )
        self.assertNotEqual(
            updated_address,
            self.test_partner,
            "A new invoicing address should have been created",
        )
        self.assertEqual(updated_address.street, "rue modifiée")
        self.assertEqual(updated_address.city, "Ville modifiée")
        self.assertEqual(updated_address.parent_id, self.test_partner)
        self.assertEqual(updated_address.type, "invoice")
        self.assertNotEqual(self.test_partner.street, "rue modifiée")
        self.assertNotEqual(self.test_partner.city, "Ville modifiée")

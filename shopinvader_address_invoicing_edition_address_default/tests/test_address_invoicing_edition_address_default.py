# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestAddressInvoicingEditionAddressDefault(SavepointCase):
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

        cls.test_partner_invoicing_address_2 = cls.env["res.partner"].create(
            {
                "name": "Invoicing Address 2",
                "street": "rue de la facturation 2",
                "zip": "75002",
                "city": "Paris",
                "country_id": cls.env.ref("base.fr").id,
                "type": "invoice",
                "parent_id": cls.test_partner.id,
            }
        )
        cls.test_partner.partner_invoice_id = cls.test_partner_invoicing_address

    def test_get_shopinvader_invoicing_addresses(self):
        invoicing_address = self.test_partner._get_shopinvader_invoicing_addresses()
        self.assertEqual(
            invoicing_address,
            self.test_partner_invoicing_address,
            "The invoicing address returned is not the expected one",
        )

    def test_get_shopinvader_invoicing_addresses_2(self):
        self.test_partner.partner_invoice_id = self.test_partner_invoicing_address_2
        invoicing_address = self.test_partner._get_shopinvader_invoicing_addresses()
        self.assertEqual(
            invoicing_address,
            self.test_partner_invoicing_address_2,
            "The invoicing address returned is not the expected one",
        )

    def test_update_shopinvader_invoicing_address(self):
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
        self.assertEqual(self.test_partner.partner_invoice_id, updated_address)

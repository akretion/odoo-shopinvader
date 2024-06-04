# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.tests.common import tagged

from .common import TestShopinvaderSettingsApiCommon


@tagged("post_install", "-at_install")
class TestShopinvaderSettingsApi(TestShopinvaderSettingsApiCommon):
    def test_get_settings(self):
        settings = self._call_test_client("/settings")
        partner_titles = settings.get("partner_titles")

        self.assertTrue(partner_titles)
        self.assertTrue(partner_titles[0].get("id"))
        self.assertTrue(partner_titles[0].get("name"))

        countries = settings.get("countries")
        self.assertTrue(countries)
        self.assertTrue(countries[0].get("id"))
        self.assertTrue(countries[0].get("code"))
        self.assertTrue(countries[0].get("name"))

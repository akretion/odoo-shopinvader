# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from fastapi import status
from requests import Response

from odoo.tests.common import tagged

from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase

from ..routers import settings_router


@tagged("post_install", "-at_install")
class TestShopinvaderSettingsApiCommon(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.PartnerTitle = cls.env["res.partner.title"]
        cls.User = cls.env["res.users"].with_context(no_reset_password=True)
        cls.user = cls.User.create(
            {
                "name": "Test User",
                "login": "test_user",
            }
        )

        cls.partner_title = cls.PartnerTitle.create({"name": "test partner title"})
        cls.default_fastapi_running_user = cls.user
        cls.default_fastapi_router = settings_router

    def _call_test_client(self, url, http_code=status.HTTP_200_OK, **kwargs):
        method = kwargs.pop("method", "get")
        with self._create_test_client(
            router=self.default_fastapi_router
        ) as test_client:
            response: Response = getattr(test_client, method)(url, **kwargs)
        self.assertEqual(
            response.status_code,
            http_code,
            msg=f"error message: {response.text}",
        )
        return response.json()

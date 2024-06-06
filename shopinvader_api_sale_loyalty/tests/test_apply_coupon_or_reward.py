# Copyright 2021 Camptocamp SA
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json
import uuid

from requests import Response

from odoo.exceptions import UserError
from odoo.tests.common import tagged

from odoo.addons.shopinvader_api_cart.routers import cart_router

from ..routers import sale_loyalty_cart_router
from .common import TestShopinvaderSaleLoyaltyCommon


@tagged("post_install", "-at_install")
class TestLoyaltyCard(TestShopinvaderSaleLoyaltyCommon):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_with_rights.groups_id = [
            (
                6,
                0,
                [
                    cls.env.ref(
                        "shopinvader_api_security_sale.shopinvader_sale_user_group"
                    ).id,
                ],
            )
        ]
        cls.cart = cls.env["sale.order"]._create_empty_cart(
            cls.default_fastapi_authenticated_partner.id
        )
        cls.dummy_uuid = str(uuid.uuid4())

    def test_code_promotion_program_generate_coupons(self):
        # 10% on code
        coupon = self._generate_coupons(self._create_program())
        with self._create_test_client(router=cart_router) as test_client:
            data = {
                "transactions": [
                    {"uuid": self.dummy_uuid, "product_id": self.product_A.id, "qty": 1}
                ]
            }
            response: Response = test_client.post("/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            len(self.cart.order_line),
            1,
            "The coupon shouldn't have been applied as the code hasn't been entered yet",
        )
        # Enter code
        with self._create_test_client(router=sale_loyalty_cart_router) as test_client:
            data = {"code": coupon.code}
            response = test_client.post("/coupon", content=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertEqual(
            len(self.cart.order_line.ids),
            2,
            "The coupon should've been applied",
        )
        self.assertEqual(res["promo_codes"], [])
        # Try to apply twice
        with self._create_test_client(
            router=sale_loyalty_cart_router
        ) as test_client, self.assertRaisesRegex(
            UserError, "This coupon has already been used"
        ):
            data = {"code": coupon.code}
            test_client.post("/coupon", content=json.dumps(data))

    def test_code_promotion_program_with_code(self):
        # 10% on code
        self._create_program("test_10pc")
        with self._create_test_client(router=cart_router) as test_client:
            data = {
                "transactions": [
                    {"uuid": self.dummy_uuid, "product_id": self.product_A.id, "qty": 1}
                ]
            }
            response: Response = test_client.post("/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            len(self.cart.order_line),
            1,
            "The coupon shouldn't have been applied as the code hasn't been entered yet",
        )
        # Enter code
        with self._create_test_client(router=sale_loyalty_cart_router) as test_client:
            data = {"code": "test_10pc"}
            response = test_client.post("/coupon", content=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertEqual(
            len(self.cart.order_line.ids),
            2,
            "The coupon should've been applied",
        )
        self.assertEqual(res["promo_codes"], ["test_10pc"])
        # Try to apply twice
        with self._create_test_client(
            router=sale_loyalty_cart_router
        ) as test_client, self.assertRaisesRegex(
            UserError, "The promo code is already applied on this order"
        ):
            data = {"code": "test_10pc"}
            test_client.post("/coupon", content=json.dumps(data))

    def test_sync_update_promotion(self):
        self._create_program(code_needed=False)
        with self._create_test_client(router=cart_router) as test_client:
            data = {
                "transactions": [
                    {"uuid": self.dummy_uuid, "product_id": self.product_A.id, "qty": 1}
                ]
            }
            test_client.post("/sync", content=json.dumps(data))
        self.assertEqual(len(self.cart.order_line), 2)
        self.assertEqual(self.cart.order_line[0].product_id, self.product_A)
        self.assertIn("Discount", self.cart.order_line[1].name)
        self.assertAlmostEqual(self.cart.amount_untaxed, 90)  # 100-10

        with self._create_test_client(router=cart_router) as test_client:
            data = {
                "transactions": [
                    {"uuid": self.dummy_uuid, "product_id": self.product_A.id, "qty": 1}
                ]
            }
            test_client.post("/sync", content=json.dumps(data))
        self.assertEqual(len(self.cart.order_line), 2)

        self.assertAlmostEqual(self.cart.amount_untaxed, 180)  # 200-20

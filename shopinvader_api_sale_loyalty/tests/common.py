# Copyright 2021 Camptocamp SA
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase
from odoo.addons.sale_coupon.tests.common import TestSaleCouponCommon


class TestShopinvaderSaleLoyaltyCommon(FastAPITransactionCase, TestSaleCouponCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.env["res.partner"].create({"name": "FastAPI Loyalty Demo"})
        cls.user_with_rights = cls.env["res.users"].create(
            {
                "name": "Test User With Rights",
                "login": "user_with_rights",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref(
                                "shopinvader_api_sale_loyalty.shopinvader_loyalty_user_group"
                            ).id,
                        ],
                    )
                ],
            }
        )
        cls.default_fastapi_running_user = cls.user_with_rights
        cls.default_fastapi_authenticated_partner = partner.with_user(
            cls.user_with_rights
        )

    def setUp(self):
        super().setUp()

    def _generate_coupons(self, program, qty=1):
        existing_coupons = program.coupon_ids

        # Create coupons
        (
            self.env["coupon.generate.wizard"]
            .with_context(active_id=program.id)
            .create(
                {
                    "generation_type": "nbr_coupon",
                    "nbr_coupons": qty,
                }
            )
            .generate_coupon()
        )
        # Return only the created coupons
        return program.coupon_ids - existing_coupons

    def _create_program(self, code=False, code_needed=True):
        return self.env["coupon.program"].create(
            {
                "name": "Code for 10% on orders",
                "promo_code_usage": "code_needed" if code_needed else "no_code_needed",
                "promo_code": code,
                "discount_type": "percentage",
                "discount_percentage": 10.0,
                "program_type": "promotion_program",
            }
        )

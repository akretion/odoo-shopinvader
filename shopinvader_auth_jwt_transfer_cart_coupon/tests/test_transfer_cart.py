# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.sale_coupon.tests.common import TestSaleCouponCommon
from odoo.addons.shopinvader_auth_jwt_transfer_cart.tests.common import (
    CommonTransferCartCase,
)


class TestTransferCart(CommonTransferCartCase, TestSaleCouponCommon):
    def test_cart_transfer_global_promo(self):
        self.env["coupon.program"].create(
            {
                "name": "10% on all products",
                "promo_code_usage": "no_code_needed",
                "discount_type": "percentage",
                "discount_percentage": 10.0,
                "program_type": "promotion_program",
                "discount_apply_on": "specific_products",
                "discount_specific_product_ids": [
                    (
                        6,
                        0,
                        [
                            self.product_3.id,
                        ],
                    )
                ],
            }
        )
        self.cart.unlink()
        self.service.dispatch("search")
        self.service.dispatch(
            "add_item", params={"product_id": self.product_1.id, "item_qty": 2}
        )
        self.service.dispatch(
            "add_item", params={"product_id": self.product_2.id, "item_qty": 1}
        )

        self.guest_cart.unlink()
        self.guest_service.dispatch("search")
        self.guest_service.dispatch(
            "add_item", params={"product_id": self.product_3.id, "item_qty": 2}
        )
        self.guest_service.dispatch(
            "add_item", params={"product_id": self.product_2.id, "item_qty": 5}
        )

        # Logged in cart
        cart = self.service.dispatch("search")["data"]
        self.assertEquals(cart["lines"]["count"], 3)

        self.assertEquals(
            cart["lines"]["items"][0]["name"],
            "[FURN_0097] Customizable Desk (CONFIG) (Steel, Black)\n160x80cm, with large legs.",
        )
        self.assertEquals(cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            cart["lines"]["items"][1]["name"], "[FURN_1118] Corner Desk Left Sit"
        )
        self.assertEquals(cart["lines"]["items"][1]["qty"], 1)

        self.assertEquals(cart["no_code_promo_program_ids"]["count"], 0)

        # Guest cart
        guest_cart = self.guest_service.dispatch("search")["data"]
        self.assertEquals(guest_cart["lines"]["count"], 7)
        self.assertEquals(
            guest_cart["lines"]["items"][0]["name"],
            "[E-COM12] Conference Chair (CONFIG) (Steel)",
        )
        self.assertEquals(guest_cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            guest_cart["lines"]["items"][1]["name"], "[FURN_1118] Corner Desk Left Sit"
        )
        self.assertEquals(guest_cart["lines"]["items"][1]["qty"], 5)

        self.assertEquals(guest_cart["no_code_promo_program_ids"]["count"], 1)
        self.assertEquals(
            guest_cart["no_code_promo_program_ids"]["items"][0]["name"],
            "10% on all products",
        )

        # Transfer guest to logged in cart

        with self._mock_request("Bearer " + self.guest_token):
            transferred_cart = self.guest_service.dispatch(
                "transfer", params={"token": self.token}
            )["data"]

        self.assertEquals(transferred_cart["lines"]["count"], 7)
        self.assertEquals(
            transferred_cart["lines"]["items"][0]["name"],
            "[E-COM12] Conference Chair (CONFIG) (Steel)",
        )
        self.assertEquals(transferred_cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            transferred_cart["lines"]["items"][1]["name"],
            "[FURN_1118] Corner Desk Left Sit",
        )
        self.assertEquals(transferred_cart["lines"]["items"][1]["qty"], 5)

        self.assertEquals(transferred_cart["no_code_promo_program_ids"]["count"], 1)
        self.assertEquals(
            transferred_cart["no_code_promo_program_ids"]["items"][0]["name"],
            "10% on all products",
        )

        self.assertEquals(self.service.dispatch("search")["data"], transferred_cart)

    def test_cart_transfer_merge_global_promo(self):
        self.backend.merge_cart_on_transfer = True
        self.env["coupon.program"].create(
            {
                "name": "10% on all products",
                "promo_code_usage": "no_code_needed",
                "discount_type": "percentage",
                "discount_percentage": 10.0,
                "program_type": "promotion_program",
                "discount_apply_on": "specific_products",
                "discount_specific_product_ids": [
                    (
                        6,
                        0,
                        [
                            self.product_1.id,
                        ],
                    )
                ],
            }
        )

        self.cart.unlink()
        self.service.dispatch("search")
        self.service.dispatch(
            "add_item", params={"product_id": self.product_1.id, "item_qty": 2}
        )
        self.service.dispatch(
            "add_item", params={"product_id": self.product_2.id, "item_qty": 1}
        )

        self.guest_cart.unlink()
        self.guest_service.dispatch("search")
        self.guest_service.dispatch(
            "add_item", params={"product_id": self.product_3.id, "item_qty": 2}
        )
        self.guest_service.dispatch(
            "add_item", params={"product_id": self.product_2.id, "item_qty": 5}
        )

        # Logged in cart
        cart = self.service.dispatch("search")["data"]
        self.assertEquals(cart["lines"]["count"], 3)

        self.assertEquals(
            cart["lines"]["items"][0]["name"],
            "[FURN_0097] Customizable Desk (CONFIG) (Steel, Black)\n160x80cm, with large legs.",
        )
        self.assertEquals(cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            cart["lines"]["items"][1]["name"], "[FURN_1118] Corner Desk Left Sit"
        )
        self.assertEquals(cart["lines"]["items"][1]["qty"], 1)

        self.assertEquals(cart["no_code_promo_program_ids"]["count"], 1)
        self.assertEquals(
            cart["no_code_promo_program_ids"]["items"][0]["name"],
            "10% on all products",
        )

        # Guest cart
        guest_cart = self.guest_service.dispatch("search")["data"]
        self.assertEquals(guest_cart["lines"]["count"], 7)
        self.assertEquals(
            guest_cart["lines"]["items"][0]["name"],
            "[E-COM12] Conference Chair (CONFIG) (Steel)",
        )
        self.assertEquals(guest_cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            guest_cart["lines"]["items"][1]["name"], "[FURN_1118] Corner Desk Left Sit"
        )
        self.assertEquals(guest_cart["lines"]["items"][1]["qty"], 5)

        self.assertEquals(guest_cart["no_code_promo_program_ids"]["count"], 0)

        # Transfer guest to logged in cart

        with self._mock_request("Bearer " + self.guest_token):
            transferred_cart = self.guest_service.dispatch(
                "transfer", params={"token": self.token}
            )["data"]

        self.assertEquals(transferred_cart["lines"]["count"], 10)
        self.assertEquals(
            transferred_cart["lines"]["items"][0]["name"],
            "[FURN_0097] Customizable Desk (CONFIG) (Steel, Black)\n160x80cm, with large legs.",
        )
        self.assertEquals(transferred_cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            transferred_cart["lines"]["items"][1]["name"],
            "[FURN_1118] Corner Desk Left Sit",
        )
        self.assertEquals(transferred_cart["lines"]["items"][1]["qty"], 6)
        self.assertEquals(
            transferred_cart["lines"]["items"][2]["name"],
            "[E-COM12] Conference Chair (CONFIG) (Steel)",
        )
        self.assertEquals(transferred_cart["lines"]["items"][2]["qty"], 2)

        self.assertEquals(self.service.dispatch("search")["data"], transferred_cart)

        self.assertEquals(transferred_cart["no_code_promo_program_ids"]["count"], 1)
        self.assertEquals(
            transferred_cart["no_code_promo_program_ids"]["items"][0]["name"],
            "10% on all products",
        )

    def test_cart_transfer_coupon(self):
        self.coupon_program = self.env["coupon.program"].create(
            {
                "name": "$5 coupon",
                "program_type": "coupon_program",
                "reward_type": "discount",
                "discount_type": "fixed_amount",
                "discount_fixed_amount": 5,
                "active": True,
                "discount_apply_on": "on_order",
            }
        )
        # Generate ONE coupon
        self.env["coupon.generate.wizard"].with_context(
            active_id=self.coupon_program.id
        ).create(
            {
                "generation_type": "nbr_coupon",
                "nbr_coupons": 1,
            }
        ).generate_coupon()
        coupon = self.coupon_program.coupon_ids

        self.cart.unlink()
        self.service.dispatch("search")
        self.service.dispatch(
            "add_item", params={"product_id": self.product_1.id, "item_qty": 2}
        )
        self.service.dispatch(
            "add_item", params={"product_id": self.product_2.id, "item_qty": 1}
        )

        self.guest_cart.unlink()
        self.guest_service.dispatch("search")
        self.guest_service.dispatch(
            "add_item", params={"product_id": self.product_3.id, "item_qty": 2}
        )
        self.guest_service.dispatch(
            "add_item", params={"product_id": self.product_2.id, "item_qty": 5}
        )
        self.guest_service.dispatch("apply_coupon", params={"code": coupon.code})

        # Logged in cart
        cart = self.service.dispatch("search")["data"]
        self.assertEquals(cart["lines"]["count"], 3)

        self.assertEquals(
            cart["lines"]["items"][0]["name"],
            "[FURN_0097] Customizable Desk (CONFIG) (Steel, Black)\n160x80cm, with large legs.",
        )
        self.assertEquals(cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            cart["lines"]["items"][1]["name"], "[FURN_1118] Corner Desk Left Sit"
        )
        self.assertEquals(cart["lines"]["items"][1]["qty"], 1)
        self.assertEquals(cart["applied_coupon_ids"]["count"], 0)

        # Guest cart
        guest_cart = self.guest_service.dispatch("search")["data"]
        self.assertEquals(guest_cart["lines"]["count"], 7)
        self.assertEquals(
            guest_cart["lines"]["items"][0]["name"],
            "[E-COM12] Conference Chair (CONFIG) (Steel)",
        )
        self.assertEquals(guest_cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            guest_cart["lines"]["items"][1]["name"], "[FURN_1118] Corner Desk Left Sit"
        )
        self.assertEquals(guest_cart["lines"]["items"][1]["qty"], 5)

        self.assertEquals(guest_cart["applied_coupon_ids"]["count"], 1)
        self.assertEquals(
            guest_cart["applied_coupon_ids"]["items"][0]["code"],
            coupon.code,
        )

        # Transfer guest to logged in cart

        with self._mock_request("Bearer " + self.guest_token):
            transferred_cart = self.guest_service.dispatch(
                "transfer", params={"token": self.token}
            )["data"]

        self.assertEquals(transferred_cart["lines"]["count"], 7)
        self.assertEquals(
            transferred_cart["lines"]["items"][0]["name"],
            "[E-COM12] Conference Chair (CONFIG) (Steel)",
        )
        self.assertEquals(transferred_cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            transferred_cart["lines"]["items"][1]["name"],
            "[FURN_1118] Corner Desk Left Sit",
        )
        self.assertEquals(transferred_cart["lines"]["items"][1]["qty"], 5)

        self.assertEquals(transferred_cart["applied_coupon_ids"]["count"], 1)
        self.assertEquals(
            transferred_cart["applied_coupon_ids"]["items"][0]["code"],
            coupon.code,
        )

        self.assertEquals(self.service.dispatch("search")["data"], transferred_cart)

    def test_cart_transfer_merge_coupon_guest(self):
        self.backend.merge_cart_on_transfer = True
        self.coupon_program = self.env["coupon.program"].create(
            {
                "name": "$5 coupon",
                "program_type": "coupon_program",
                "reward_type": "discount",
                "discount_type": "fixed_amount",
                "discount_fixed_amount": 5,
                "active": True,
                "discount_apply_on": "on_order",
            }
        )
        # Generate ONE coupon
        self.env["coupon.generate.wizard"].with_context(
            active_id=self.coupon_program.id
        ).create(
            {
                "generation_type": "nbr_coupon",
                "nbr_coupons": 1,
            }
        ).generate_coupon()
        coupon = self.coupon_program.coupon_ids

        self.cart.unlink()
        self.service.dispatch("search")
        self.service.dispatch(
            "add_item", params={"product_id": self.product_1.id, "item_qty": 2}
        )
        self.service.dispatch(
            "add_item", params={"product_id": self.product_2.id, "item_qty": 1}
        )

        self.guest_cart.unlink()
        self.guest_service.dispatch("search")
        self.guest_service.dispatch(
            "add_item", params={"product_id": self.product_3.id, "item_qty": 2}
        )
        self.guest_service.dispatch(
            "add_item", params={"product_id": self.product_2.id, "item_qty": 5}
        )
        self.guest_service.dispatch("apply_coupon", params={"code": coupon.code})

        # Logged in cart
        cart = self.service.dispatch("search")["data"]
        self.assertEquals(cart["lines"]["count"], 3)

        self.assertEquals(
            cart["lines"]["items"][0]["name"],
            "[FURN_0097] Customizable Desk (CONFIG) (Steel, Black)\n160x80cm, with large legs.",
        )
        self.assertEquals(cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            cart["lines"]["items"][1]["name"], "[FURN_1118] Corner Desk Left Sit"
        )
        self.assertEquals(cart["lines"]["items"][1]["qty"], 1)
        self.assertEquals(cart["applied_coupon_ids"]["count"], 0)

        # Guest cart
        guest_cart = self.guest_service.dispatch("search")["data"]
        self.assertEquals(guest_cart["lines"]["count"], 7)
        self.assertEquals(
            guest_cart["lines"]["items"][0]["name"],
            "[E-COM12] Conference Chair (CONFIG) (Steel)",
        )
        self.assertEquals(guest_cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            guest_cart["lines"]["items"][1]["name"], "[FURN_1118] Corner Desk Left Sit"
        )
        self.assertEquals(guest_cart["lines"]["items"][1]["qty"], 5)

        self.assertEquals(guest_cart["applied_coupon_ids"]["count"], 1)
        self.assertEquals(
            guest_cart["applied_coupon_ids"]["items"][0]["code"],
            coupon.code,
        )

        # Transfer guest to logged in cart

        with self._mock_request("Bearer " + self.guest_token):
            transferred_cart = self.guest_service.dispatch(
                "transfer", params={"token": self.token}
            )["data"]

        self.assertEquals(transferred_cart["lines"]["count"], 10)
        self.assertEquals(
            transferred_cart["lines"]["items"][0]["name"],
            "[FURN_0097] Customizable Desk (CONFIG) (Steel, Black)\n160x80cm, with large legs.",
        )
        self.assertEquals(transferred_cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            transferred_cart["lines"]["items"][1]["name"],
            "[FURN_1118] Corner Desk Left Sit",
        )
        self.assertEquals(transferred_cart["lines"]["items"][1]["qty"], 6)
        self.assertEquals(
            transferred_cart["lines"]["items"][2]["name"],
            "[E-COM12] Conference Chair (CONFIG) (Steel)",
        )
        self.assertEquals(transferred_cart["applied_coupon_ids"]["count"], 1)
        self.assertEquals(
            transferred_cart["applied_coupon_ids"]["items"][0]["code"],
            coupon.code,
        )

        self.assertEquals(transferred_cart["lines"]["items"][2]["qty"], 2)

    def test_cart_transfer_merge_coupon_partner(self):
        self.backend.merge_cart_on_transfer = True
        self.coupon_program = self.env["coupon.program"].create(
            {
                "name": "$5 coupon",
                "program_type": "coupon_program",
                "reward_type": "discount",
                "discount_type": "fixed_amount",
                "discount_fixed_amount": 5,
                "active": True,
                "discount_apply_on": "on_order",
            }
        )
        # Generate ONE coupon
        self.env["coupon.generate.wizard"].with_context(
            active_id=self.coupon_program.id
        ).create(
            {
                "generation_type": "nbr_coupon",
                "nbr_coupons": 1,
            }
        ).generate_coupon()
        coupon = self.coupon_program.coupon_ids

        self.cart.unlink()
        self.service.dispatch("search")
        self.service.dispatch(
            "add_item", params={"product_id": self.product_1.id, "item_qty": 2}
        )
        self.service.dispatch(
            "add_item", params={"product_id": self.product_2.id, "item_qty": 1}
        )
        self.service.dispatch("apply_coupon", params={"code": coupon.code})

        self.guest_cart.unlink()
        self.guest_service.dispatch("search")
        self.guest_service.dispatch(
            "add_item", params={"product_id": self.product_3.id, "item_qty": 2}
        )
        self.guest_service.dispatch(
            "add_item", params={"product_id": self.product_2.id, "item_qty": 5}
        )

        # Logged in cart
        cart = self.service.dispatch("search")["data"]
        self.assertEquals(cart["lines"]["count"], 3)

        self.assertEquals(
            cart["lines"]["items"][0]["name"],
            "[FURN_0097] Customizable Desk (CONFIG) (Steel, Black)\n160x80cm, with large legs.",
        )
        self.assertEquals(cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            cart["lines"]["items"][1]["name"], "[FURN_1118] Corner Desk Left Sit"
        )
        self.assertEquals(cart["lines"]["items"][1]["qty"], 1)

        self.assertEquals(cart["applied_coupon_ids"]["count"], 1)
        self.assertEquals(
            cart["applied_coupon_ids"]["items"][0]["code"],
            coupon.code,
        )

        # Guest cart
        guest_cart = self.guest_service.dispatch("search")["data"]
        self.assertEquals(guest_cart["lines"]["count"], 7)
        self.assertEquals(
            guest_cart["lines"]["items"][0]["name"],
            "[E-COM12] Conference Chair (CONFIG) (Steel)",
        )
        self.assertEquals(guest_cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            guest_cart["lines"]["items"][1]["name"], "[FURN_1118] Corner Desk Left Sit"
        )
        self.assertEquals(guest_cart["lines"]["items"][1]["qty"], 5)

        self.assertEquals(guest_cart["applied_coupon_ids"]["count"], 0)

        # Transfer guest to logged in cart

        with self._mock_request("Bearer " + self.guest_token):
            transferred_cart = self.guest_service.dispatch(
                "transfer", params={"token": self.token}
            )["data"]

        self.assertEquals(transferred_cart["lines"]["count"], 10)
        self.assertEquals(
            transferred_cart["lines"]["items"][0]["name"],
            "[FURN_0097] Customizable Desk (CONFIG) (Steel, Black)\n160x80cm, with large legs.",
        )
        self.assertEquals(transferred_cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            transferred_cart["lines"]["items"][1]["name"],
            "[FURN_1118] Corner Desk Left Sit",
        )
        self.assertEquals(transferred_cart["lines"]["items"][1]["qty"], 6)
        self.assertEquals(
            transferred_cart["lines"]["items"][2]["name"],
            "[E-COM12] Conference Chair (CONFIG) (Steel)",
        )
        self.assertEquals(transferred_cart["applied_coupon_ids"]["count"], 1)
        self.assertEquals(
            transferred_cart["applied_coupon_ids"]["items"][0]["code"],
            coupon.code,
        )

        self.assertEquals(transferred_cart["lines"]["items"][2]["qty"], 2)

    def test_cart_transfer_merge_cancelled_coupon_guest(self):
        self.backend.merge_cart_on_transfer = True
        self.coupon_program = self.env["coupon.program"].create(
            {
                "name": "$5 coupon",
                "program_type": "coupon_program",
                "reward_type": "discount",
                "discount_type": "fixed_amount",
                "discount_fixed_amount": 5,
                "active": True,
                "discount_apply_on": "on_order",
            }
        )
        # Generate ONE coupon
        self.env["coupon.generate.wizard"].with_context(
            active_id=self.coupon_program.id
        ).create(
            {
                "generation_type": "nbr_coupon",
                "nbr_coupons": 1,
            }
        ).generate_coupon()
        coupon = self.coupon_program.coupon_ids

        self.cart.unlink()
        self.service.dispatch("search")
        self.service.dispatch(
            "add_item", params={"product_id": self.product_1.id, "item_qty": 2}
        )
        self.service.dispatch(
            "add_item", params={"product_id": self.product_2.id, "item_qty": 1}
        )

        self.guest_cart.unlink()
        self.guest_service.dispatch("search")
        self.guest_service.dispatch(
            "add_item", params={"product_id": self.product_3.id, "item_qty": 2}
        )
        self.guest_service.dispatch(
            "add_item", params={"product_id": self.product_2.id, "item_qty": 5}
        )
        self.guest_service.dispatch("apply_coupon", params={"code": coupon.code})
        coupon.write({"state": "cancel"})

        # Logged in cart
        cart = self.service.dispatch("search")["data"]
        self.assertEquals(cart["lines"]["count"], 3)

        self.assertEquals(
            cart["lines"]["items"][0]["name"],
            "[FURN_0097] Customizable Desk (CONFIG) (Steel, Black)\n160x80cm, with large legs.",
        )
        self.assertEquals(cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            cart["lines"]["items"][1]["name"], "[FURN_1118] Corner Desk Left Sit"
        )
        self.assertEquals(cart["lines"]["items"][1]["qty"], 1)
        self.assertEquals(cart["applied_coupon_ids"]["count"], 0)

        # Guest cart
        guest_cart = self.guest_service.dispatch("search")["data"]
        self.assertEquals(guest_cart["lines"]["count"], 7)
        self.assertEquals(
            guest_cart["lines"]["items"][0]["name"],
            "[E-COM12] Conference Chair (CONFIG) (Steel)",
        )
        self.assertEquals(guest_cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            guest_cart["lines"]["items"][1]["name"], "[FURN_1118] Corner Desk Left Sit"
        )
        self.assertEquals(guest_cart["lines"]["items"][1]["qty"], 5)

        self.assertEquals(guest_cart["applied_coupon_ids"]["count"], 1)
        self.assertEquals(
            guest_cart["applied_coupon_ids"]["items"][0]["code"],
            coupon.code,
        )

        # Transfer guest to logged in cart

        with self._mock_request("Bearer " + self.guest_token):
            transferred_cart = self.guest_service.dispatch(
                "transfer", params={"token": self.token}
            )["data"]

        self.assertEquals(transferred_cart["lines"]["count"], 10)
        self.assertEquals(
            transferred_cart["lines"]["items"][0]["name"],
            "[FURN_0097] Customizable Desk (CONFIG) (Steel, Black)\n160x80cm, with large legs.",
        )
        self.assertEquals(transferred_cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            transferred_cart["lines"]["items"][1]["name"],
            "[FURN_1118] Corner Desk Left Sit",
        )
        self.assertEquals(transferred_cart["lines"]["items"][1]["qty"], 6)
        self.assertEquals(
            transferred_cart["lines"]["items"][2]["name"],
            "[E-COM12] Conference Chair (CONFIG) (Steel)",
        )
        self.assertEquals(transferred_cart["applied_coupon_ids"]["count"], 0)

        self.assertEquals(transferred_cart["lines"]["items"][2]["qty"], 2)

    def test_cart_transfer_merge_cancelled_coupon_partner(self):
        self.backend.merge_cart_on_transfer = True
        self.coupon_program = self.env["coupon.program"].create(
            {
                "name": "$5 coupon",
                "program_type": "coupon_program",
                "reward_type": "discount",
                "discount_type": "fixed_amount",
                "discount_fixed_amount": 5,
                "active": True,
                "discount_apply_on": "on_order",
            }
        )
        # Generate ONE coupon
        self.env["coupon.generate.wizard"].with_context(
            active_id=self.coupon_program.id
        ).create(
            {
                "generation_type": "nbr_coupon",
                "nbr_coupons": 1,
            }
        ).generate_coupon()
        coupon = self.coupon_program.coupon_ids

        self.cart.unlink()
        self.service.dispatch("search")
        self.service.dispatch(
            "add_item", params={"product_id": self.product_1.id, "item_qty": 2}
        )
        self.service.dispatch(
            "add_item", params={"product_id": self.product_2.id, "item_qty": 1}
        )
        self.service.dispatch("apply_coupon", params={"code": coupon.code})
        coupon.write({"state": "cancel"})

        self.guest_cart.unlink()
        self.guest_service.dispatch("search")
        self.guest_service.dispatch(
            "add_item", params={"product_id": self.product_3.id, "item_qty": 2}
        )
        self.guest_service.dispatch(
            "add_item", params={"product_id": self.product_2.id, "item_qty": 5}
        )

        # Logged in cart
        cart = self.service.dispatch("search")["data"]
        self.assertEquals(cart["lines"]["count"], 3)

        self.assertEquals(
            cart["lines"]["items"][0]["name"],
            "[FURN_0097] Customizable Desk (CONFIG) (Steel, Black)\n160x80cm, with large legs.",
        )
        self.assertEquals(cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            cart["lines"]["items"][1]["name"], "[FURN_1118] Corner Desk Left Sit"
        )
        self.assertEquals(cart["lines"]["items"][1]["qty"], 1)

        self.assertEquals(cart["applied_coupon_ids"]["count"], 1)
        self.assertEquals(
            cart["applied_coupon_ids"]["items"][0]["code"],
            coupon.code,
        )

        # Guest cart
        guest_cart = self.guest_service.dispatch("search")["data"]
        self.assertEquals(guest_cart["lines"]["count"], 7)
        self.assertEquals(
            guest_cart["lines"]["items"][0]["name"],
            "[E-COM12] Conference Chair (CONFIG) (Steel)",
        )
        self.assertEquals(guest_cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            guest_cart["lines"]["items"][1]["name"], "[FURN_1118] Corner Desk Left Sit"
        )
        self.assertEquals(guest_cart["lines"]["items"][1]["qty"], 5)

        self.assertEquals(guest_cart["applied_coupon_ids"]["count"], 0)

        # Transfer guest to logged in cart

        with self._mock_request("Bearer " + self.guest_token):
            transferred_cart = self.guest_service.dispatch(
                "transfer", params={"token": self.token}
            )["data"]

        self.assertEquals(transferred_cart["lines"]["count"], 10)
        self.assertEquals(
            transferred_cart["lines"]["items"][0]["name"],
            "[FURN_0097] Customizable Desk (CONFIG) (Steel, Black)\n160x80cm, with large legs.",
        )
        self.assertEquals(transferred_cart["lines"]["items"][0]["qty"], 2)
        self.assertEquals(
            transferred_cart["lines"]["items"][1]["name"],
            "[FURN_1118] Corner Desk Left Sit",
        )
        self.assertEquals(transferred_cart["lines"]["items"][1]["qty"], 6)
        self.assertEquals(
            transferred_cart["lines"]["items"][2]["name"],
            "[E-COM12] Conference Chair (CONFIG) (Steel)",
        )
        self.assertEquals(transferred_cart["applied_coupon_ids"]["count"], 1)
        self.assertEquals(
            transferred_cart["applied_coupon_ids"]["items"][0]["code"],
            coupon.code,
        )
        self.assertEquals(transferred_cart["lines"]["items"][2]["qty"], 2)

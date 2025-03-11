# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import CommonTransferCartCase


class TestTransferCart(CommonTransferCartCase):
    def test_cart_transfer_only(self):
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

        self.assertEquals(self.service.dispatch("search")["data"], transferred_cart)

    def test_cart_transfer_merge(self):
        self.backend.merge_cart_on_transfer = True

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

    def test_cart_transfer_merge_no_cart(self):
        self.backend.merge_cart_on_transfer = True

        self.cart.unlink()

        self.guest_cart.unlink()
        self.guest_service.dispatch("search")
        self.guest_service.dispatch(
            "add_item", params={"product_id": self.product_3.id, "item_qty": 2}
        )
        self.guest_service.dispatch(
            "add_item", params={"product_id": self.product_2.id, "item_qty": 5}
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

        self.assertEquals(self.service.dispatch("search")["data"], transferred_cart)

    def test_cart_transfer_with_partner_email_duplicates(self):
        self.backend.merge_cart_on_transfer = True
        self.env["shopinvader.partner"].create(
            {
                "name": "Homomail",
                "email": self.partner.email,
                "backend_id": self.env.ref("shopinvader.backend_2").id,
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

    def test_cart_transfer_with_bad_products(self):
        self.backend.merge_cart_on_transfer = True

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

        # Forbid product_3
        self.product_3.shopinvader_bind_ids.unlink()
        # Transfer guest to logged in cart
        with self._mock_request("Bearer " + self.guest_token):
            transferred_cart = self.guest_service.dispatch(
                "transfer", params={"token": self.token}
            )["data"]

        self.assertEquals(transferred_cart["lines"]["count"], 8)
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

        self.assertEquals(self.service.dispatch("search")["data"], transferred_cart)

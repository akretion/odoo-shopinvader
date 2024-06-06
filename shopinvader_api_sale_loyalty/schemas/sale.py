# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tools.safe_eval import safe_eval

from odoo.addons.shopinvader_schema_sale.schemas import Sale as BaseSale

from ..schemas import Coupon, CouponProgram


class Sale(BaseSale, extends=True):
    promo_codes: list[str] = []
    reward_amount: float = 0
    reward_amount_tax_incl: float = 0
    programs: list[CouponProgram] = []
    generated_coupons: list[Coupon] = []
    claimable_rewards: list = []

    @classmethod
    def from_sale_order(cls, odoo_rec):
        obj = super().from_sale_order(odoo_rec)
        obj.promo_codes = [odoo_rec.promo_code] if odoo_rec.promo_code else []
        obj.reward_amount = odoo_rec.reward_amount
        obj.reward_amount_tax_incl = sum(
            [
                line.price_subtotal + line.price_tax
                for line in odoo_rec._get_reward_lines()
            ]
        )

        obj.programs = [
            CouponProgram.from_coupon_program(program)
            for program in odoo_rec.no_code_promo_program_ids
            | odoo_rec.code_promo_program_id
        ]
        obj.generated_coupons = [
            Coupon.from_coupon(coupon)
            for coupon in odoo_rec.applied_coupon_ids | odoo_rec.generated_coupon_ids
        ]
        return obj

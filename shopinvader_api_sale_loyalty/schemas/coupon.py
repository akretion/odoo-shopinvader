# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from extendable_pydantic import StrictExtendableBaseModel


class CouponInput(StrictExtendableBaseModel):
    code: str


class Coupon(StrictExtendableBaseModel):
    id: int
    code: str

    @classmethod
    def from_coupon(cls, coupon):
        return cls(id=coupon.id, code=coupon.code)


class CouponProgram(StrictExtendableBaseModel):
    id: int
    name: str

    @classmethod
    def from_coupon_program(cls, program):
        return cls(id=program.id, name=program.name)

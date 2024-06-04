# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from extendable_pydantic import StrictExtendableBaseModel

from .country import Country
from .partner_title import PartnerTitle


class Settings(StrictExtendableBaseModel):
    countries: list[Country] = []
    partner_titles: list[PartnerTitle] = []

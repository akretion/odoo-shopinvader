# Copyright 2026 Akretion (http://www.akretion.com).
# @author Benoît Guillot <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_api_settings.schemas.country import Country as BaseCountry


class Country(BaseCountry, extends=True):
    """Flag the countries for which the eInvoicing applies.

    The flag is set for every country code that represents France (France and
    DOM-TOM), as the French eInvoicing relies on the directory of the French
    business directory.
    """

    einvoicing: bool = False

    @classmethod
    def from_res_country(cls, odoo_rec):
        res = super().from_res_country(odoo_rec)
        fr_country_codes = odoo_rec.env["res.company"]._get_france_country_codes()
        res.einvoicing = bool(odoo_rec.code and odoo_rec.code in fr_country_codes)
        return res

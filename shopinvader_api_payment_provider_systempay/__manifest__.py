# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Shopinvader Api Payment Provider Systempay",
    "summary": """
        Specific routes for systempay payments from Shopinvader""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "fastapi",
        "shopinvader_api_payment",
        "payment_systempay",
    ],
    "data": [],
    "demo": [],
}

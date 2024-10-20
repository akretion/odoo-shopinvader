# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Address Api Firstname",
    "summary": """
        Adds fields firstname lastname in address schemas""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion,Odoo Community Association (OCA)",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "shopinvader_api_address",
        "partner_firstname",
    ],
    "data": [],
    "external_dependencies": {
        "python": ["fastapi", "extendable_pydantic>=1.0.0", "pydantic>=2.0.0"]
    },
    "installable": True,
}

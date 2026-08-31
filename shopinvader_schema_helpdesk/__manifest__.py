# Copyright 2026 Akretion (https://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "shopinvader Schema Helpdesk",
    "summary": "Shopinvader Schema for Helpdesk",
    "version": "18.0.1.0.0",
    "development_status": "Alpha",
    "category": "Shopinvader",
    "maintainers": ["hparfr"],
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": " Akretion",
    "license": "AGPL-3",
    "depends": [
        "helpdesk_mgmt",
        "helpdesk_mgmt_sale",
        "pydantic",
        "extendable",
    ],
    "external_dependencies": {
        "python": ["extendable_pydantic>=1.2.0", "pydantic>=2.0.0"],
    },
    "installable": True,
}

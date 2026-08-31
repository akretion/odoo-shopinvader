# Copyright 2026 Akretion (https://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader API Helpdesk",
    "summary": "Provides helpdesk api via Fastapi",
    "version": "18.0.1.0.0",
    "development_status": "Alpha",
    "category": "Uncategorized",
    "maintainers": ["hparfr"],
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Akretion",
    "license": "AGPL-3",
    "depends": [
        "shopinvader_router_helper",
        "shopinvader_schema_helpdesk",
        "helpdesk_mgmt_sale",
        "extendable_fastapi",
    ],
    "installable": True,
}

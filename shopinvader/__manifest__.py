# Copyright 2023 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Shopinvader",
    "summary": "Shopinvader",
    "version": "16.0.1.0.0",
    "category": "e-commerce",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Akretion",
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "depends": [
        "product",
        "sale",
        "server_environment",
    ],
    "data": [
        "security/shopinvader_security.xml",
        "security/ir.model.access.csv",
        "security/shopinvader_backend_security.xml",
        "data/ir_export_category.xml",
        "data/ir_export_product.xml",
        "views/menu.xml",
        "views/shopinvader_backend.xml",
    ],
}

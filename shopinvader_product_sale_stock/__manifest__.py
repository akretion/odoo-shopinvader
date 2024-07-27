# Copyright 2018 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Shopinvader Product Sale Stock",
    "summary": "This module is used to add sale info depending on stock",
    "version": "14.0.1.0.0",
    "category": "e-commerce",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Akretion",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["shopinvader_product_stock_state"],
    "data": [
#        "views/shopinvader_backend.xml",
#        "views/shopinvader_product.xml",
        "data/ir_export_product.xml",
    ],

}

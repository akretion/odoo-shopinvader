# Copyright 2024 Akretion (http://www.akretion.com)
# Olivier Nibart <olivier.nibart@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Shopinvader Optional Product",
    "summary": "Export optional products",
    "version": "14.0.0.0.1",
    "category": "e-commerce",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Akretion",
    "license": "AGPL-3",
    "depends": [
        "shopinvader",
        "sale_product_configurator",
        "shopinvader_image",
        "base_sparse_field",
    ],
    "data": [
        "data/ir_export_product.xml",
    ],
    "installable": True,
}

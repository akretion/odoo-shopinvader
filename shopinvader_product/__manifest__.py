# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Product",
    "summary": """Adds shopinvader product fields and schemas""",
    "version": "16.0.1.0.3",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "base_sparse_field",
        "product",
        "pydantic",
        "extendable",
    ],
    "data": ["views/product_category.xml", "views/product_template.xml"],
    "demo": [
        "demo/product_category.xml",
        "demo/product_attribute_value.xml",
        "demo/product_product.xml",
    ],
    "external_dependencies": {
        "python": ["extendable_pydantic>=1.2.0", "pydantic>=2.0.0", "unidecode"]
    },
    "installable": True,
    "development_status": "Alpha",
}

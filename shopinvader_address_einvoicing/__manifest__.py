# Copyright 2026 Akretion (http://www.akretion.com).
# @author Benoît Guillot <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Address eInvoicing",
    "summary": "Expose the French eInvoicing directory of the customer on the "
    "addresses managed by the Shopinvader API",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion,Odoo Community Association (OCA)",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "l10n_fr_einvoicing",
        "shopinvader_api_address",
        "shopinvader_api_settings",
    ],
    "data": [
        "security/acl_directory_line.xml",
    ],
    "installable": True,
}

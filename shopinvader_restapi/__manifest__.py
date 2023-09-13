# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
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
    "external_dependencies": {"python": ["cerberus", "unidecode"], "bin": []},
    "depends": [
        "base_rest",
        "jsonifier",
        "base_sparse_field_list_support",
        "base_vat",
        "component_event",
        "sale",
        "sale_discount_display_amount",
        "server_environment",
        "onchange_helper",
        "queue_job",
        "mail",
        "base",
        "shopinvader",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/shopinvader_partner_security.xml",
        "wizards/shopinvader_partner_binding.xml",
        "views/shopinvader_cart_step_view.xml",
        "views/shopinvader_partner_view.xml",
        "views/res_config_settings.xml",
        "views/sale_view.xml",
        "views/shopinvader_sale_view.xml",
        "views/partner_view.xml",
        "data/res_partner.xml",
        "data/cart_step.xml",
        "data/mail_activity_data.xml",
        "data/queue_job_channel_data.xml",
        "data/queue_job_function_data.xml",
    ],
    "demo": [
        "demo/account_demo.xml",
        "demo/pricelist_demo.xml",
        "demo/backend_demo.xml",
        "demo/partner_demo.xml",
        "demo/sale_demo.xml",
        "demo/email_demo.xml",
        "demo/notification_demo.xml",
    ],
    "qweb": [],
    "pre_init_hook": "pre_init_hook",
}

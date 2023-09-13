{
    "name": "Shopinvader Helpdesk",
    "summary": "Integrate Helpdesk into Shopinvader",
    "version": "16.0.1.0.0",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": " Akretion",
    "license": "AGPL-3",
    "depends": [
        "pydantic",
        "extendable",
        "extendable_fastapi",
        "fastapi",
        "shopinvader",
        "shopinvader_auth_api_key",
        "helpdesk_mgmt",
        "helpdesk_mgmt_sale",  # Sale info on helpdesk tickets
    ],
    "external_dependencies": {
        "python": [
            "fastapi",
            "pydantic>=2.0.0",
            "pydantic[email]",
            "extendable-pydantic>=1.1.0",
        ]
    },
    "data": [
        # "security/helpdesk_security.xml",
        # "security/ir.model.access.csv",
        # "views/helpdesk_settings.xml",
        "data/fastapi_endpoint.xml",
    ],
    "installable": True,
}

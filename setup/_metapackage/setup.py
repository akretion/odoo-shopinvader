import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-shopinvader-odoo-shopinvader",
    description="Meta package for shopinvader-odoo-shopinvader Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-base_url',
        'odoo12-addon-shopinvader',
        'odoo12-addon-shopinvader_algolia',
        'odoo12-addon-shopinvader_assortment',
        'odoo12-addon-shopinvader_backend_image_proxy',
        'odoo12-addon-shopinvader_delivery_carrier',
        'odoo12-addon-shopinvader_elasticsearch',
        'odoo12-addon-shopinvader_guest_mode',
        'odoo12-addon-shopinvader_image',
        'odoo12-addon-shopinvader_lead',
        'odoo12-addon-shopinvader_locomotive',
        'odoo12-addon-shopinvader_locomotive_guest_mode',
        'odoo12-addon-shopinvader_partner_vat',
        'odoo12-addon-shopinvader_product_stock',
        'odoo12-addon-shopinvader_quotation',
        'odoo12-addon-shopinvader_search_engine',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)

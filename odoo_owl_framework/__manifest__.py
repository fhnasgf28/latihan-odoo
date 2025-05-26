{
    'name': "odoo_owl_framework",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'website', 'sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/todo_assets.xml',
        'views/owl_assets.xml',
        'views/sale_order_views.xml',
        # 'views/owl_crud_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'odoo_owl_framework/static/src/**',
            # "odoo_owl_framework/static/src/js/note_app.js",
        ],
        'web.assets_backend': [
            # 'odoo_owl_framework/static/src/components/order_type_dropdown.js',
            'odoo_owl_framework/static/src/components/templates.xml',
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}


{
    'name': "face_recognition",

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
    'depends': ['base', 'hr', 'hr_attendance', 'web'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'wizard/recognition_wizard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'face_recognition/static/src/js/camera_widget.js',
            'face_recognition/static/src/js/entry_point.js',
            'face_recognition/static/src/xml/camera_template.xml',
            'face_recognition/static/src/components/camera_widget/camera_widget.xml',
        ],
    },
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
}


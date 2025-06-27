{
    'name': 'Gemini Chat',
    'version': '17.0.1.0.0',
    'category': 'Tools',
    'summary': 'Integrasi Chat dengan Google Gemini API',
    'description': """
        Modul untuk mengintegrasikan Google Gemini AI dengan Odoo
    """,
    'author': 'Your Name',
    'website': 'https://www.yourwebsite.com',
    'depends': ['base', 'web', 'external_api_caller', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/gemini_chat_views.xml',
        'views/gemini_chat_menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

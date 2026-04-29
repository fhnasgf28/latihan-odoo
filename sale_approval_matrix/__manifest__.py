{
    'name': 'Sales Order Approval Matrix',
    'version': '1.1',
    'category': 'Sales',
    'summary': 'Dynamic approval matrix for Sales Orders based on amount ranges.',
    'description': """
        This module adds an approval layer to Sales Orders.
        Approval is triggered based on defined amount ranges in the Approval Matrix.
        Includes delegation (substitution) features for approvers and global configuration.
    """,
    'author': 'Farhan Assegaf',
    'depends': ['sale'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/sale_order_rejection_wizard_view.xml',
        'views/sale_approval_matrix_views.xml',
        'views/sale_order_views.xml',
        'views/res_users_delegation_views.xml',
        'views/sales_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

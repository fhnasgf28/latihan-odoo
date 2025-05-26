from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_type = fields.Selection([
        ('retail', 'Retail'),
        ('wholesale', 'Wholesale'),
        ('custom', 'Custom Order'),
    ], string="Order Type")

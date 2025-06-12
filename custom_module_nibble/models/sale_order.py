from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_tolerance = fields.Float(string="Delivery Tolerance",help="Maximum delivery tolerance allowed, e.g., 5 means 5%.")

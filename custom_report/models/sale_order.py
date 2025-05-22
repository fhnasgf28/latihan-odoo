from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def print_custom_sales_report(self):
        return self.env.ref('custom_report.action_custom_sale_report').report_action(self)

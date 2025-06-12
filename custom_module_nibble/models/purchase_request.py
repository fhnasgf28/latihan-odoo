from odoo import models, fields

class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    notes = fields.Text(string="Notes")

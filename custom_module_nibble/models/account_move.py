from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    nsfp = fields.Char(string="Nomor Seri Faktur Pajak (NSFP)")

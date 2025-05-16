from odoo import models, fields, api
import random


class ResPartner(models.Model):
    _inherit = 'res.partner'

    default_package = fields.Selection([
        ('paket_a', 'Paket 1 - 100.000'),
        ('paket_b', 'Paket 2 - 150.000'),
        ('paket_c', 'Paket 3 - 200.000'),
    ], string='Paket Internet', default='paket_a')
    address_code = fields.Char(string='Kode Alamat')
    wifi_customer_number = fields.Char(string="Nomor Pelanggan", copy=False, readonly=True)
    wifi_billing_id = fields.Many2one('wifi.billing', string='Wifi Billing', copy=False, readonly=True)

    @api.onchange('street')
    def _onchange_street(self):
        if self.street:
            self.address_code = self.street[:3].upper()
        else:
            self.address_code = ''

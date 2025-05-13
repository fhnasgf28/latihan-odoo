from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    default_package = fields.Selection([
        ('paket_a', 'Paket 1 - 100.000'),
        ('paket_b', 'Paket 2 - 150.000'),
        ('paket_c', 'Paket 3 - 200.000'),
    ], string='Paket Internet', default='paket_a')


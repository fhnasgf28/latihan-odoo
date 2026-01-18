from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RentalAsset(models.Model):
    _name = 'rental.asset'
    _description = 'Rental Asset'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True, tracking=True)
    asset_tag = fields.Char(required=True, tracking=True)
    serial_no = fields.Char(index=True)
    category_id = fields.Many2one('product.category', string='Category')
    state = fields.Selection([
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('maintenance', 'Maintenance'),
        ('retired', 'Retired'),
    ], default='available', tracking=True, required=True)
    rental_price_day = fields.Monetary(string='Price / Day', required=True, default=0.0)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id.id)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True)
    active_rental_order_id = fields.Many2one('rental.order', string='Active Rental Order', compute='_compute_active_rental_order_id', store=False)

    def _compute_active_rental_order_id(self):
        for asset in self:
            order_line = self.env['rental.order.line'].search([
                ('asset_id', '=', asset.id),
                ('order.state', 'in', ['approved', 'on_rent', 'to_approve']),
                ], limit=1, order='id desc')
            asset.active_rental_order_id = order_line.order_id if order_line else False

    @api.constrains('rental_price_day')
    def _check_price(self):
        for rec in self:
            if rec.rental_price_day < 0:
                raise ValidationError(_('Price cannot be negative'))
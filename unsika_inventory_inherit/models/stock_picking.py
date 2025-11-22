from odoo import models, fields, api
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # 1. Field untuk menampung total nilai barang di DO ini
    total_value = fields.Monetary(
        string="Total Value",
        compute='_compute_total_value',
        store=True,
        currency_field='company_currency_id'
    )

    # Field bantuan untuk mata uang (required by Monetary field)
    company_currency_id = fields.Many2one(
        related='company_id.currency_id',
        string="Company Currency",
        readonly=True
    )

    # 2. Field Penanda: Apakah ini barang SULTAN?
    is_high_value = fields.Boolean(
        string="Is High Value Shipment",
        compute='_compute_high_value',
        store=True,
        help="True jika total nilai barang di atas 10 Juta"
    )

    # LOGIC MENGHITUNG NILAI (The Brain)
    @api.depends('move_ids.product_id', 'move_ids.product_uom_qty')
    def _compute_total_value(self):
        for picking in self:
            total = 0.0
            # Kita loop setiap baris barang yang mau dikirim
            for line in picking.move_ids:
                # Asumsi: Ambil harga dari List Price (Sales Price) product
                total += line.product_id.list_price * line.product_uom_qty
            picking.total_value = total

    # LOGIC MENENTUKAN STATUS SULTAN
    @api.depends('total_value')
    def _compute_high_value(self):
        limit = 10000000  # Batas 10 Juta
        for picking in self:
            # Jika total lebih dari 10jt, set True
            picking.is_high_value = (picking.total_value > limit)

    def button_validate(self):
        if self.is_high_value:
            is_manager = self.env.user.has_group('stock.group_stock_manager')
            if is_manager:
                raise UserError(
                    "⛔ AKSES DITOLAK! ⛔\n\n"
                    "Ini adalah pengiriman bernilai tinggi (> 10 Juta).\n"
                    "Hanya Manager Inventory yang boleh melakukan Validasi.\n"
                    "Panggil bosmu sekarang!"
                )
        return super(StockPicking, self).button_validate()
from odoo import fields, models, api 
from odoo.exceptions import ValidationError, UserError
from odoo.addons.base_utils.logger import get_logger, log_testing1, log_usererror,log_testing2, log_testing3
logger = get_logger(__name__)


class GudangPengeluaran(models.Model):
    _name = 'gudang.pengeluaran'
    _description = 'Pengeluaran / Pengiriman Barang'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'nomor'
    _order = 'tanggal desc, id desc'

    nomor = fields.Char(
        string='No. Pengeluaran',
        required=True, copy=False, readonly=True, default='New',
    )
    tanggal = fields.Date(
        string='Tanggal Pengeluaran',
        required=True, default=fields.Date.context_today, tracking=True,
    )
    nama_penerima = fields.Char(string='Nama Penerima / Customer', tracking=True)
    tujuan = fields.Char(string='Tujuan Pengiriman', tracking=True)
    no_dokumen_ref = fields.Char(string='No. Dokumen Referensi')
    lokasi_asal_id = fields.Many2one('gudang.lokasi', string="Lokasi Asal (Gudang)")
    tipe_pengeluaran = fields.Selection([
        ('penjualan',  '💰 Penjualan'),
        ('transfer',   '🔄 Transfer Antar Gudang'),
        ('retur',      '↩️ Retur ke Supplier'),
        ('pemakaian',  '🔧 Pemakaian Internal'),
        ('lainnya',    '📋 Lainnya'),
    ], string='Tipe Pengeluaran', default='penjualan', required=True, tracking=True)

    state = fields.Selection([
        ('draft',      '📝 Draft'),
        ('konfirmasi', '✅ Dikonfirmasi'),
        ('done',       '✔️ Selesai'),
        ('cancel',     '❌ Dibatalkan'),
    ], string='Status', default='draft', tracking=True, copy=False)
    line_ids = fields.One2many('gudang.pengeluaran.line', 'pengeluaran_id', string='Detail Barang', copy=True)
    total_item  = fields.Integer(string='Total Jenis Barang', compute='_compute_total', store=True)
    total_qty   = fields.Float(string='Total Qty', compute='_compute_total', store=True)
    total_nilai = fields.Float(string='Total Nilai (Rp)', compute='_compute_total', store=True, digits=(16,2))
    catatan = fields.Text(string='Catatan')
    petugas_id = fields.Many2one('res.users', string='Petugas', default=lambda self: self.env.user)

    @api.depends('line_ids.qty_keluar', 'line_ids.harga_satuan')
    def _compute_total(self):
        for rec in self:
            rec.total_item = len(rec.line_ids)
            rec.total_qty = sum(line.qty_keluar for line in rec.line_ids)
            log_testing1(logger, f"Hitung total untuk pengeluaran ~{rec.nomor}~: Total Item=~{rec.total_item}~, Total Qty=~{rec.total_qty}~")
            rec.total_nilai = sum(line.qty_keluar * line.harga_satuan for line in rec.line_ids) 
            log_testing2(logger, f"Hitung total nilai untuk pengeluaran ~{rec.nomor}~: Total Nilai=~{rec.total_nilai}~")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('nomor', 'New') == 'New':
                vals['nomor'] = self.env['ir.sequence'].next_by_code('gudang.pengeluaran') or 'PGN-00001'
        return super().create(vals_list)

class GudangPengeluaranLine(models.Model):
    _name = 'gudang.pengeluaran.line'
    _description = 'Detail Baris Pengeluaran Barang'

    pengeluaran_id = fields.Many2one(
        'gudang.pengeluaran',
        string='Dokumen Pengeluaran',
        required=True,
        ondelete='cascade',
        index=True,
    )
    produk_id = fields.Many2one('gudang.produk', string='Produk', required=True)

    # Related fields dari produk
    satuan = fields.Selection(related='produk_id.satuan', string='Satuan', readonly=True)
    stok_tersedia = fields.Float(related='produk_id.stok_tersedia', string='Stok Tersedia', readonly=True)
    lot_id = fields.Many2one('gudang.lot', string='Lot/Batch', domain="[('produk_id', '=', produk_id), ('state', 'not in', ['recall', 'habis']), ('qty_sisa', '>', 0)]")
    # Related fields dari header (pengeluaran_id)
    tanggal = fields.Date(related='pengeluaran_id.tanggal', string='Tanggal', readonly=True, store=True)
    state = fields.Selection(related='pengeluaran_id.state', string='Status', readonly=True)

    qty_keluar = fields.Float(string='Qty Keluar', required=True, default=1.0)
    harga_satuan = fields.Float(string='Harga Satuan', digits=(16, 2))
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)

    lokasi_asal_id = fields.Many2one(
        'gudang.lokasi',
        string='Lokasi Asal',
        related='pengeluaran_id.lokasi_asal_id',
        store=True,
    )

    keterangan = fields.Char(string='Keterangan')

    @api.depends('qty_keluar', 'harga_satuan')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.qty_keluar * rec.harga_satuan
    
    @api.onchange('produk_id')
    def _onchange_produk_id(self):
        if self.produk_id:
            self.harga_satuan = self.produk_id.harga_jual
        
    @api.constrains('qty_keluar')
    def _check_qty_keluar(self):
        for rec in self:
            if rec.qty_keluar <= 0:
                log_usererror(logger, f"gagal menyimpan detail pengeluaran untuk produk ~{rec.produk_id.name}~: qty keluar harus lebih dari 0")
                raise ValidationError("Qty keluar harus lebih dari 0.")
            if rec.qty_keluar > rec.stok_tersedia:
                log_usererror(logger, f"gagal menyimpan detail pengeluaran untuk produk ~{rec.produk_id.name}~: qty keluar ({rec.qty_keluar}) melebihi stok tersedia ({rec.stok_tersedia})")
                raise ValidationError(f"Qty keluar ({rec.qty_keluar}) tidak boleh melebihi stok tersedia ({rec.stok_tersedia}).")
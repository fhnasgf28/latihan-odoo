from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from odoo.addons.base_utils.logger import get_logger, log_testing1, log_usererror,log_testing2, log_testing3

logger = get_logger(__name__)

class GudangPenerimaan(models.Model):
    _name = 'gudang.penerimaan'
    _description = 'Penerimaan Barang'
    _rec_name = 'nomor'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'tanggal desc, id desc'

    # ─── FIELD HEADER ────────────────────────────────────────────────
    nomor = fields.Char(
        string='No. Penerimaan',
        required=True,
        copy=False,
        readonly=True,
        default='New',
    )
    tanggal = fields.Date(
        string='Tanggal Penerimaan',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    nama_supplier = fields.Char(string='Nama Supplier', tracking=True)
    no_surat_jalan = fields.Char(string='No. Surat Jalan', tracking=True)
    lokasi_tujuan_id = fields.Many2one(
        'gudang.lokasi',
        string='Lokasi Tujuan',
        required=True,
        domain=[('tipe_lokasi', 'in', ['gudang', 'rak'])],
        tracking=True,
    )

    # ─── STATE MACHINE ───────────────────────────────────────────────
    state = fields.Selection([
        ('draft',      '📝 Draft'),
        ('konfirmasi', '✅ Dikonfirmasi'),
        ('done',       '✔️ Selesai'),
        ('cancel',     '❌ Dibatalkan'),
    ], string='Status', default='draft', tracking=True, copy=False)
    line_ids = fields.One2many(
        'gudang.penerimaan.line',
        'penerimaan_id',
        string='Detail Barang',
    )

    # ─── FIELD COMPUTED ──────────────────────────────────────────────
    total_item = fields.Integer(
        string='Total Jenis Barang',
        compute='_compute_total',
        store=True,
    )
    total_qty = fields.Float(
        string='Total Qty',
        compute='_compute_total',
        store=True,
    )
    total_nilai = fields.Float(
        string='Total Nilai (Rp)',
        compute='_compute_total',
        store=True,
        digits=(16, 2),
    )
    catatan = fields.Text(string='Catatan')
    petugas_id = fields.Many2one('res.users', string='Petugas', default=lambda self: self.env.user)

    @api.depends('line_ids.produk_id', 'line_ids.qty_diterima', 'line_ids.harga_satuan')
    def _compute_total(self):
        for rec in self:
            rec.total_item = len(rec.line_ids)
            rec.total_qty = sum(rec.line_ids.mapped('qty_diterima'))
            log_testing1(logger, f"menghitung total qty untuk penerimaan ~{rec.nomor}~: ~{rec.total_qty}~")
            rec.total_nilai = sum(line.subtotal for line in rec.line_ids)
            log_testing2(logger, f"menghitung total nilai untuk penerimaan ~{rec.nomor}~: ~{rec.total_nilai}~")
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('nomor', 'New') == 'New':
                vals['nomor'] = self.env['ir.sequence'].next_by_code('gudang.penerimaan') or 'New'
        records = super().create(vals_list)
        log_testing3(logger, f"membuat penerimaan baru dengan nomor: {[rec.nomor for rec in records]}~")
        return records

    def action_konfirmasi(self):
        for rec in self: 
            if not rec.line_ids:
                log_usererror(logger, f"gagal mengkonfirmasi penerimaan ~{rec.nomor}~: tidak ada detail barang")
                raise UserError("Tidak bisa konfirmasi penerimaan tanpa detail barang.")
            for line in rec.line_ids:
                if line.qty_diterima <= 0:
                    log_usererror(logger, f"gagal mengkonfirmasi penerimaan ~{rec.nomor}~: qty diterima untuk produk ~{line.produk_id.name}~ harus lebih dari 0")
                    raise UserError(f"Qty diterima untuk produk '{line.produk_id.name}' harus lebih dari 0.")
        self.write({'state': 'konfirmasi'})
        log_testing1(logger, f"menerapkan status 'konfirmasi' pada penerimaan ~{rec.nomor}~")

    def action_validasi(self):
        for rec in self:
            if rec.state != 'konfirmasi':
                log_usererror(logger, f"gagal memvalidasi penerimaan ~{rec.nomor}~: status harus 'konfirmasi' untuk validasi")
                raise UserError("Hanya penerimaan dengan status 'konfirmasi' yang bisa divalidasi.")
            # Update stok produk
            rec.state = 'done'
            rec.line_ids.produk_id._compute_stok_tersedia()
        log_testing1(logger, f"menerapkan status 'done' pada penerimaan ~{rec.nomor}~")
    
    def action_cancel(self):
        for rec in self:
            if rec.state == 'done':
                log_usererror(logger, f"gagal membatalkan penerimaan ~{rec.nomor}~: tidak bisa membatalkan penerimaan yang sudah selesai")
                raise UserError("Tidak bisa membatalkan penerimaan yang sudah selesai.")
            rec.state = 'cancel'
        log_testing1(logger, f"menerapkan status 'cancel' pada penerimaan ~{rec.nomor}~")
    
    def action_reset_draft(self):
        for rec in self:
            if rec.state != 'cancel':
                log_usererror(logger, f"gagal mengembalikan penerimaan ~{rec.nomor}~ ke draft: hanya penerimaan yang dibatalkan yang bisa dikembalikan ke draft")
                raise UserError("Hanya penerimaan yang dibatalkan yang bisa dikembalikan ke draft.")
            rec.state = 'draft'
        log_testing1(logger, f"menerapkan status 'draft' pada penerimaan ~{rec.nomor}~")

class GudangPenerimaanLine(models.Model):
    """
    Model LINE / Detail dari penerimaan
    Setiap baris mewakili satu produk yang diterima
    """
    _name = 'gudang.penerimaan.line'
    _description = 'Detail Baris Penerimaan Barang'

    # Many2one ke header: setiap line MILIK SATU penerimaan
    # ondelete='cascade': jika header dihapus, semua line ikut terhapus
    penerimaan_id = fields.Many2one(
        'gudang.penerimaan',
        string='Dokumen Penerimaan',
        required=True,
        ondelete='cascade',
        index=True,
    )

    # Many2one ke produk
    produk_id = fields.Many2one(
        'gudang.produk',
        string='Produk',
        required=True,
    )

    # Related field: ambil data dari produk terkait
    satuan = fields.Selection(related='produk_id.satuan', string='Satuan', readonly=True)
    stok_sekarang = fields.Float(related='produk_id.stok_tersedia', string='Stok Saat Ini', readonly=True)

    # Related fields dari header (penerimaan_id)
    tanggal = fields.Date(related='penerimaan_id.tanggal', string='Tanggal', readonly=True, store=True)
    state = fields.Selection(related='penerimaan_id.state', string='Status', readonly=True)

    qty_pesan = fields.Float(string='Qty Dipesan', default=1.0)
    qty_diterima = fields.Float(string='Qty Diterima', required=True, default=1.0)
    harga_satuan = fields.Float(string='Harga Satuan', digits=(16, 2))
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)

    lokasi_tujuan_id = fields.Many2one(
        'gudang.lokasi',
        string='Lokasi Tujuan',
        related='penerimaan_id.lokasi_tujuan_id',
        store=True,
    )

    keterangan = fields.Char(string='Keterangan')
    expired_date = fields.Date(string='Tgl Kadaluarsa')

    @api.depends('qty_diterima', 'harga_satuan')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.qty_diterima * rec.harga_satuan
    
    @api.onchange('produk_id')
    def _onchange_produk_id(self):
        if self.produk_id:
            self.harga_satuan = self.produk_id.harga_beli


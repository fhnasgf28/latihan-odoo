from odoo import models, fields, api 
from odoo.exceptions import ValidationError
from odoo.addons.base_utils.logger import get_logger, log_testing1, log_usererror,log_testing2, log_testing3
logger = get_logger(__name__)

class GudangProduct(models.Model):
    _name = 'gudang.produk'
    _description = 'Master Product Gudang'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'

    # ─── FIELD IDENTITAS ────────────────────────────────────────────
    name = fields.Char(
        string='Nama Produk',
        required=True,
        tracking=True,   # tracking=True agar setiap perubahan tercatat di chatter
        index=True,
    )
    kode_produk = fields.Char(
        string='Kode Produk',
        copy=False,
        readonly=True,
        default='New',
    )
    barcode = fields.Char(string='Barcode', copy=False)
    active = fields.Boolean(default=True, tracking=True)
    kategori_id = fields.Many2one("gudang.kategori.produk")
    satuan = fields.Selection([
        ('pcs',  'PCS / Buah'),
        ('kg',   'Kilogram'),
        ('liter','Liter'),
        ('meter','Meter'),
        ('box',  'Box / Karton'),
        ('set',  'Set'),
    ], string='Satuan', default='pcs', required=True, tracking=True)
    # ─── FIELD HARGA ────────────────────────────────────────────────
    harga_beli = fields.Float(string='Harga Beli (HPP)', digits=(16, 2), tracking=True)
    harga_jual = fields.Float(string='Harga Jual', digits=(16, 2), tracking=True)

    # ─── FIELD STOK ─────────────────────────────────────────────────
    stok_minimum = fields.Float(string='Stok Minimum', default=0.0)
    stok_maksimum = fields.Float(string='Stok Maksimum', default=0.0)
    # Computed field: total stok dari semua lokasi
    stok_tersedia = fields.Float(
        string='Stok Tersedia',
        compute='_compute_stok_tersedia',
        store=True,  # store=True agar bisa di-search & di-filter
    )
    penerimaan_line_ids = fields.One2many('gudang.penerimaan.line', 'produk_id', string='Riwayat Penerimaan')
    pengeluaran_line_ids = fields.One2many('gudang.pengeluaran.line', 'produk_id', string='Riwayat Pengeluaran')
    # ─── FIELD DESKRIPSI ─────────────────────────────────────────────
    deskripsi = fields.Text(string='Deskripsi')
    gambar = fields.Binary(string='Foto Produk', attachment=True)

    
    # ─── STATUS STOK ─────────────────────────────────────────────────
    status_stok = fields.Selection([
        ('aman',      '✅ Stok Aman'),
        ('menipis',   '⚠️ Stok Menipis'),
        ('habis',     '🔴 Stok Habis'),
        ('berlebih',  '📦 Stok Berlebih'),
    ], string='Status Stok', compute='_compute_status_stok', store=True)
    last_cost = fields.Float(string='Last Cost', digits=(16, 2), readonly=True, compute='_compute_last_cost', store=True)
    last_purchase_date = fields.Date(string='Last Purchase Date', readonly=True, compute='_compute_last_cost', store=True)

    @api.depends('penerimaan_line_ids.qty_diterima', 'pengeluaran_line_ids.qty_keluar')
    def _compute_stok_tersedia(self):
        for rec in self:
            total_masuk = sum(line.qty_diterima for line in rec.penerimaan_line_ids if line.penerimaan_id.state == 'done')
            total_keluar = sum(line.qty_keluar for line in rec.pengeluaran_line_ids if line.pengeluaran_id.state == 'done')
            rec.stok_tersedia = total_masuk - total_keluar
            log_testing1(logger, f"Hitung stok '~{rec.name}~': Masuk=~{total_masuk}~, Keluar=~{total_keluar}~, Tersedia=~{rec.stok_tersedia}~")


    @api.depends('stok_tersedia', 'stok_minimum', 'stok_maksimum')
    def _compute_status_stok(self):
        for rec in self:
            if rec.stok_tersedia <= 0:
                rec.status_stok = 'habis'
            elif rec.stok_tersedia <= rec.stok_minimum:
                rec.status_stok = 'menipis'
            elif rec.stok_tersedia >= rec.stok_maksimum:
                rec.status_stok = 'berlebih'
            else:
                rec.status_stok = 'aman'
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('kode_produk', 'New') == 'New':
                vals['kode_produk'] = self.env['ir.sequence'].next_by_code('gudang.produk') or 'New'
        return super().create(vals_list)

    def name_get(self):
        result = []
        for rec in self:
            name = f"[{rec.kode_produk}] {rec.name}"
            result.append((rec.id, name))
        return result

    @api.constrains('stok_minimum', 'stok_maksimum')
    def _check_stok_limits(self):
        for rec in self:
            if rec.stok_maksimum > 0 and rec.stok_maksimum < rec.stok_minimum:
                raise ValidationError("Stok maksimum harus lebih besar atau sama dengan stok minimum.")

    @api.depends('penerimaan_line_ids.penerimaan_id.tanggal')
    def _compute_last_cost(self):
        for rec in self:
            # Use existing one2many recordset and sort in Python to avoid
            # SQL property handling for dotted order ('penerimaan_id.tanggal')
            log_testing1(logger, f"Menghitung last cost untuk produk ~{rec.name}~ berdasarkan penerimaan terbaru")
            lines = rec.penerimaan_line_ids.filtered(lambda l: l.harga_satuan)
            if lines:
                sorted_lines = sorted(lines, key=lambda l: (l.penerimaan_id.tanggal or l.create_date), reverse=True)
                line = sorted_lines[0]
                rec.last_cost = line.harga_satuan
                rec.last_purchase_date = line.penerimaan_id.tanggal or (line.create_date and fields.Date.to_date(line.create_date))
            else:
                rec.last_cost = 0.0
                rec.last_purchase_date = False


class GudangKategoriProduk(models.Model):
    """Sub-model kategori produk"""
    _name = 'gudang.kategori.produk'
    _description = 'Kategori Produk Gudang'
    _parent_name = 'parent_id'  # support hierarki kategori
    _parent_store = True
    _rec_name = 'complete_name'

    name = fields.Char(string='Nama Kategori', required=True)
    parent_id = fields.Many2one('gudang.kategori.produk', string='Kategori Induk', ondelete='restrict')
    child_ids = fields.One2many('gudang.kategori.produk', 'parent_id', string='Sub-Kategori')
    parent_path = fields.Char(index=True)
    complete_name = fields.Char(compute='_compute_complete_name', store=True)

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for rec in self:
            if rec.parent_id:
                rec.complete_name = f"{rec.parent_id.complete_name} / {rec.name}"
            else:
                rec.complete_name = rec.name


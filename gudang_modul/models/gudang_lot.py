from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError

class GudangLot(models.Model):
    _name = 'gudang.lot'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Lot/Batch Produk'

    name = fields.Char(
        string='Nomor Lot',
        required=True,
        default='New',
        readonly=True,
        copy=False,
        tracking=True,
        index=True,
    )
    produk_id = fields.Many2one('gudang.produk', string='Produk', required=True, ondelete='restrict', tracking=True, index=True)
    tanggal_expired = fields.Date(string='Tanggal Kadaluarsa', tracking=True)
    qty = fields.Float(string='Qty', required=True, default=1.0)
    satuan = fields.Selection(related='produk_id.satuan', string='Satuan', readonly=True)
    tanggal_produksi = fields.Date(string='Tanggal Produksi', tracking=True)
    penerimaan_line_ids = fields.One2many('gudang.penerimaan.line', 'lot_id', string='Riwayat Masuk')
    nama_supplier = fields.Char(string='Nama Supplier / Produsen')
    no_batch_supplier = fields.Char(string='No. Batch Supplier')
    qty_masuk = fields.Float(string='Qty Masuk', compute='_compute_qty', store=True, digits=(16, 2))
    qty_keluar = fields.Float(string='Qty Keluar', compute='_compute_qty', store=True, digits=(16, 2))
    qty_sisa = fields.Float(string='Qty Sisa', compute='_compute_qty', store=True, digits=(16, 2))
    pengeluaran_line_ids = fields.One2many('gudang.pengeluaran.line', 'lot_id', string='Riwayat Keluar')
    state = fields.Selection([
        ('aktif',    '✅ Aktif'),
        ('expired',  '⚠️ Kadaluarsa'),
        ('habis',    '📭 Habis'),
        ('recall',   '🚨 Recall'),
    ], string='Status', default='aktif', tracking=True)
    is_expired = fields.Boolean(string='Sudah Expired ?', compute='_compute_is_expired', store=True)
    sisa_hari = fields.Integer(string='Sisa Hari Sebelum Expired', compute='_compute_is_expired', store=True)
    catatan = fields.Text(string='Catatan')
    active = fields.Boolean(default=True, tracking=True)

    @api.depends(
        'penerimaan_line_ids.qty_diterima',
        'penerimaan_line_ids.penerimaan_id.state',
        'pengeluaran_line_ids.qty_keluar',
        'pengeluaran_line_ids.pengeluaran_id.state',
    )
    def _compute_qty(self):
        for rec in self:
            rec.qty_masuk = sum(line.qty_diterima for line in rec.penerimaan_line_ids if line.penerimaan_id.state in ['done', 'diterima'])
            rec.qty_keluar = sum(line.qty_keluar for line in rec.pengeluaran_line_ids if line.pengeluaran_id.state in ['done', 'diterima'])
            rec.qty_sisa = rec.qty_masuk - rec.qty_keluar
    
    @api.depends('tanggal_expired')
    def _compute_is_expired(self):
        hari_ini = date.today()
        for rec in self:
            if rec.tanggal_expired:
                delta = (rec.tanggal_expired - hari_ini).days
                rec.sisa_hari = delta
                rec.is_expired = delta < 0
            else:
                rec.sisa_hari = 0
                rec.is_expired = False
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('gudang.lot') or 'New Lot'
        return super().create(vals_list)

    def action_recall(self):
        for rec in self:
            rec.state = 'recall'
            # chatter
            rec.message_post(body=f"Lot {rec.name} telah di-RECALL. Semua transaksi terkait lot ini harus diperiksa kembali.")
    
    def action_set_aktif(self):
        for rec in self:
            rec.state = 'aktif'
            # chatter
            rec.message_post(body=f"Lot {rec.name} telah di-set AKTIF kembali.")
    
    def action_tandai_habis(self):
        for rec in self:
            rec.state = 'habis'
            # chatter
            rec.message_post(body=f"Lot {rec.name} telah ditandai HABIS.")
    
    def name_get(self):
        result = []
        for rec in self:
            name = f"{rec.name} - {rec.produk_id.name}"
            if rec.tanggal_expired:
                name += f" (Exp: {rec.tanggal_expired})"
            result.append((rec.id, name))
        return result

    @api.constrains('tanggal_expired', 'tanggal_produksi')
    def _check_dates(self):
        for rec in self:
            if rec.tanggal_expired and rec.tanggal_produksi:
                if rec.tanggal_expired < rec.tanggal_produksi:
                    raise ValidationError("Tanggal Kadaluarsa tidak boleh lebih awal dari Tanggal Produksi.")
    
    _sql_constraints = [
        ('name_produk_uniq', 'unique(name, produk_id)', 'Nomor Lot harus unik untuk setiap produk!'),
    ]

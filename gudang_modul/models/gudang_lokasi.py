from odoo import models, fields, api 

class GudangLokasi(models.Model):
    _name = 'gudang.lokasi'
    _description = 'Gudang Lokasi / penyimpanan barang'
    _parent_name = 'parent_id'
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'

    name = fields.Char(string='Nama Lokasi', required=True)
    parent_id = fields.Many2one('gudang.lokasi', string='Lokasi Induk', ondelete='restrict', index=True)
    child_ids = fields.One2many('gudang.lokasi', 'parent_id', string='Lokasi Anak')
    parent_path = fields.Char(index=True)
    complete_name = fields.Char(string='Nama Lengkap', compute='_compute_complete_name', store=True)
    tipe_lokasi = fields.Selection([
        ('gudang',   '🏭 Gudang'),
        ('rak',      '📦 Rak / Shelving'),
        ('virtual',  '🔄 Virtual (Transit/Adjustment)'),
        ('supplier', '🚚 Supplier'),
        ('customer', '👤 Customer'),
    ], string='Tipe Lokasi', required=True, default='gudang')
    active = fields.Boolean(string='Aktif', default=True)
    keterangan = fields.Text(string='Keterangan')
    total_produk = fields.Integer(string='Total Produk', compute='_compute_total_produk')

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for rec in self:
            if rec.parent_id:
                rec.complete_name = f"{rec.parent_id.complete_name} / {rec.name}"
            else:
                rec.complete_name = rec.name

    @api.depends('child_ids', 'child_ids.total_produk')
    def _compute_total_produk(self):
        for rec in self:
            penerimaan_lines = self.env['gudang.penerimaan.line'].search(
                [('lokasi_tujuan_id', '=', rec.id), ('penerimaan_id.state', '=', 'done')])
            rec.total_produk = len(penerimaan_lines.mapped('produk_id'))
    
    _sql_constraints = [
        ('name_parent_uniq', 'UNIQUE(name, parent_id)', 'Nama lokasi harus unik dalam satu induk yang sama!'),
    ]
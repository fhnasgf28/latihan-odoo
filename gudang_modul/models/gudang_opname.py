from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.addons.base_utils.logger import get_logger, log_testing1, log_usererror,log_testing2, log_testing3

logger = get_logger(__name__)

class GudangOpname(models.Model):
    _name = 'gudang.opname'
    _description = 'Gudang Opname'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'nomor'
    _order = 'tanggal desc'

    nomor = fields.Char(string='Nomor Opname', required=True, copy=False, readonly=True, default=lambda self: 'New')
    tanggal = fields.Date(string='Tanggal Opname', required=True, default=fields.Date.context_today)
    lokasi_id = fields.Many2one('gudang.lokasi', string='Lokasi Opname', tracking=True, domain="[('tipe_lokasi', 'in', ['gudang', 'rak'])]")
    state = fields.Selection([
        ('draft',      '📝 Draft'),
        ('progress',   '🔍 Sedang Dihitung'),
        ('done',       '✔️ Selesai'),
        ('cancel',     '❌ Dibatalkan'),
    ], string='Status', default='draft', tracking=True, copy=False)
    line_ids = fields.One2many('gudang.opname.line', 'opname_id', string='Detail Opname')
    total_selisih_plus  = fields.Float(string='Total Selisih (+)', compute='_compute_summary', store=True)
    total_selisih_minus = fields.Float(string='Total Selisih (-)', compute='_compute_summary', store=True)
    ada_selisih         = fields.Boolean(string='Ada Selisih?', compute='_compute_summary', store=True)

    catatan     = fields.Text(string='Catatan')
    petugas_id  = fields.Many2one('res.users', string='Petugas', default=lambda self: self.env.user)

    @api.depends('line_ids.selisih_qty')
    def _compute_summary(self):
        for rec in self:
            selisih_plus = sum(l.selisih_qty for l in rec.line_ids if l.selisih_qty > 0)
            selisih_minus = sum(l.selisih_qty for l in rec.line_ids if l.selisih_qty < 0)
            rec.total_selisih_plus = selisih_plus
            rec.total_selisih_minus = abs(selisih_minus)
            rec.ada_selisih = bool(selisih_plus or selisih_minus)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('nomor', 'New') == 'New':
                vals['nomor'] = self.env['ir.sequence'].next_by_code('gudang.opname') or 'OPN-00001'
        return super().create(vals_list)

    def action_mulai_hitung(self):
        if not self.line_ids:
            raise UserError("Tidak bisa mulai hitung opname tanpa detail produk!")
        self.state = 'progress'
    
    def action_load_produk(self):
        for rec in self:
            if rec.state not in ('draft', 'progress'):
                raise UserError("Hanya bisa load produk untuk opname yang berstatus Draft atau Sedang Dihitung!")
        semua_produk = self.env['gudang.produk'].search([('active', '=', True)])
        existing_produk_ids = rec.line_ids.mapped('produk_id').ids
        new_lines = []
        for produk in semua_produk:
            if produk.id not in existing_produk_ids:
                new_lines.append({
                    'opname_id': rec.id,
                    'produk_id': produk.id,
                    'qty_sistem': produk.stok_tersedia,
                    'qty_fisik': produk.stok_tersedia,
                })
        if new_lines:
            self.env['gudang.opname.line'].create(new_lines)
    
    def action_validasi(self):
        for rec in self:
            if rec.state != 'progress':
                raise UserError("Hanya bisa validasi opname yang berstatus Progress!")
            lines_dengan_selisih = rec.line_ids.filtered(lambda l: l.selisih_qty != 0)
            if lines_dengan_selisih:
                lines_plus = lines_dengan_selisih.filtered(lambda l: l.selisih_qty > 0)
                if lines_plus:
                    lokasi_adj = self.env['gudang.lokasi'].search([('tipe_lokasi', '=', 'virtual')], limit=1)
                    penerimaan = self.env['gudang.penerimaan'].create({
                        'nama_suplier': f'adjusment opname {rec.nomor}',
                        'lokasi_tujuan_id': rec.lokasi_id.id or lokasi_adj.id,
                        'line_ids': [(0, 0, {
                            'produk_id': l.produk_id.id,
                            'qty_diterima': l.selisih_qty,
                            'harga_satuan': l.produk_id.harga_beli,
                        }) for l in lines_plus],
                    })
                    penerimaan.action_konfirmasi()
                    penerimaan.action_validasi()
                
                #buat satu dokumen pengeluaran untuk semua selisih kurang (-)
                lines_minus = lines_dengan_selisih.filtered(lambda l: l.selisih_qty < 0)
                if lines_minus:
                    lokasi_adj = self.env['gudang.lokasi'].search([], limit=1)
                    pengeluaran = self.env['gudang.pengeluaran'].create({
                        'nama_customer': f'adjusment opname {rec.nomor}',
                        'lokasi_asal_id': rec.lokasi_id.id or lokasi_adj.id,
                        'line_ids': [(0, 0, {
                            'produk_id': l.produk_id.id,
                            'qty_keluar': abs(l.selisih_qty),
                            'harga_satuan': l.produk_id.harga_jual,
                        }) for l in lines_minus],
                    })
                    pengeluaran.action_konfirmasi()
                    pengeluaran.action_validasi()
            rec.state = 'done'


class GudangOpnameLine(models.Model):
    _name = 'gudang.opname.line'
    _description = 'Detail Baris Stok Opname'

    opname_id = fields.Many2one('gudang.opname', string='Opname', required=True, ondelete='cascade')
    produk_id = fields.Many2one('gudang.produk', string='Produk', required=True)

    satuan       = fields.Selection(related='produk_id.satuan', string='Satuan', readonly=True)
    qty_sistem   = fields.Float(string='Qty Sistem (Teori)', digits=(16, 3))
    qty_fisik    = fields.Float(string='Qty Fisik (Lapangan)', digits=(16, 3))

    # Selisih = Fisik - Sistem
    # Positif = barang bertambah (temuan)
    # Negatif = barang berkurang (hilang)
    selisih_qty  = fields.Float(
        string='Selisih',
        compute='_compute_selisih',
        store=True,
    )
    status_selisih = fields.Selection([
        ('sesuai',    '✅ Sesuai'),
        ('lebih',     '📈 Lebih'),
        ('kurang',    '📉 Kurang'),
    ], string='Kondisi', compute='_compute_selisih', store=True)

    keterangan = fields.Char(string='Keterangan')

    @api.depends('qty_sistem', 'qty_fisik')
    def _compute_selisih(self):
        for rec in self:
            rec.selisih_qty = rec.qty_fisik - rec.qty_sistem
            if rec.selisih_qty == 0:
                rec.status_selisih = 'sesuai'
            elif rec.selisih_qty > 0:
                rec.status_selisih = 'lebih'
            else:                
                rec.status_selisih = 'kurang'


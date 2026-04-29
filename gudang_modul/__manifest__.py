# -*- coding: utf-8 -*-
{
    'name': 'Gudang Modul - Sistem Inventory',
    'version': '19.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Modul Inventory Custom untuk Latihan Odoo 19',
    'description': """
        Modul inventory custom dengan nama model berbeda dari Odoo standard.
        Mencakup:
        - Manajemen Produk (gudang.produk)
        - Manajemen Gudang/Lokasi (gudang.lokasi)
        - Penerimaan Barang / Purchase Receipt (gudang.penerimaan)
        - Pengeluaran Barang / Delivery Order (gudang.pengeluaran)
        - Stok Opname / Stock Taking (gudang.opname)
        - Laporan Kartu Stok
    """,
    'author': 'Latihan Odoo 19',
    'website': 'https://www.example.com',
    'depends': [
        'base',
        'mail',
        'product',
    ],
    'data': [
        # Security
        'security/gudang_security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/gudang_sequence.xml',

        # Views
        'views/gudang_produk_views.xml',
        'views/gudang_lokasi_views.xml',
        'views/gudang_penerimaan_views.xml',
        'views/gudang_pengeluaran_views.xml',
        'views/gudang_opname_views.xml',
        'views/gudang_menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

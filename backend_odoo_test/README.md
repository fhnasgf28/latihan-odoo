📦 Material Management Integrated (Odoo 14)
🚀 Gambaran Umum Proyek
Modul Material Management Integrated adalah solusi komprehensif untuk mengelola material mentah (raw materials) dalam ekosistem Odoo 14 Anda. Berbeda dengan pendekatan tradisional yang hanya menggunakan modul Product bawaan, modul ini memperkenalkan model Material khusus yang terintegrasi secara cerdas dengan fungsionalitas Inventory (Stock) dan Purchases Odoo standar.

Ini memungkinkan Anda untuk:

Memiliki entitas khusus untuk material dengan atribut yang relevan.
Secara otomatis mengelola produk terkait di modul Product Odoo.
Melihat kuantitas stok Material secara real-time yang diambil dari data Inventory Odoo.
Melacak riwayat pembelian Material berdasarkan Purchase Orders Odoo.
Mengatur siklus hidup Material melalui workflow status yang jelas.
✨ Fitur Utama
Model Material Khusus: Definisi Material dengan field unik seperti Material Code, Material Type (Fabric, Jeans, Cotton), Material Buy Price, Unit of Measure, Minimum Stock Quantity, dan Lifecycle Stage.
Integrasi Otomatis dengan Modul Odoo Standar:
Setiap Material secara otomatis membuat dan terhubung ke satu Product.Product di modul Odoo Product bawaan.
Perubahan pada Material (nama, kode, harga, UoM) akan otomatis memperbarui Product terkait.
Manajemen stok dan pembelian material dilakukan sepenuhnya melalui modul Inventory dan Purchases Odoo standar.
Informasi Stok & Pembelian Real-time:
Current Stock Quantity: Field terkomputasi yang menampilkan stok material saat ini, diambil langsung dari qty_available di Product.Product terkait.
Last Purchase Date: Field terkomputasi yang menunjukkan tanggal pembelian terakhir material, diambil dari Purchase Order Line terkait di Odoo.
Workflow Status Material: Implementasi state (Draft, Approved, Archived) dengan button transisi di form view untuk mengelola siklus hidup material secara terkontrol.
Validasi Data Kuat:
Validasi untuk Material Buy Price dan Material Code yang unik.
Validasi untuk memastikan setiap Material memiliki Product terkait yang unik.
Manajemen Supplier: Default Supplier yang secara otomatis terhubung sebagai Vendor pada Product terkait.
Pengelolaan Otomatis Material Code: Penomoran kode material secara otomatis saat pembuatan.
Pelacakan Komunikasi: Integrasi mail.thread dan mail.activity.mixin untuk diskusi dan aktivitas pada setiap record Material.
🛠️ Instalasi
Untuk menginstal modul ini di Odoo 14 Anda:

Clone repositori ini ke dalam direktori addons Odoo Anda.
Bash

git clone https://github.com/your_username/material_management_integrated.git /path/to/odoo/addons/material_registration
(Ganti /path/to/odoo/addons/material_registration dengan jalur sebenarnya ke direktori addons Anda dan your_username dengan username GitHub Anda.)
Perbarui Daftar Aplikasi di Odoo.
Aktifkan Developer Mode.
Pergi ke Apps -> Update Apps List.
Cari dan Instal modul "Material Management Integrated".
📖 Penggunaan
Setelah instalasi, Anda akan menemukan menu baru "Material Management" di Odoo Anda.

Membuat Material Baru:
Navigasi ke Material Management -> Materials.
Klik Create.
Isi detail material seperti Material Code (bisa otomatis), Material Name, Material Type, Material Buy Price, Default Supplier, dan Unit of Measure.
Saat disimpan, sistem akan otomatis membuat Product terkait di modul Product Odoo.
Anda bisa melihat Current Stock Quantity dan Last Purchase Date yang akan diperbarui secara otomatis berdasarkan transaksi Product terkait.
Mengelola Stok Material:
Stok material Anda dikelola melalui Product terkait di modul Inventory Odoo standar.
Navigasi ke Inventory -> Products -> Products, cari material Anda (Anda bisa memfilter Is a Material Product).
Lakukan penerimaan atau pengiriman stok seperti biasa melalui Inventory Adjustments, Receipts, dll. Current Stock Quantity pada record Material Anda akan diperbarui.
Melakukan Pembelian Material:
Pembelian material dilakukan melalui modul Purchases Odoo standar.
Navigasi ke Purchases -> Requests for Quotation.
Buat RFQ baru dan tambahkan Product material Anda ke Order Lines.
Setelah Purchase Order dikonfirmasi, Last Purchase Date pada record Material Anda akan diperbarui.
Mengubah Status Material:
Pada form view Material, gunakan button di bagian header:
Approve: Mengubah status dari Draft ke Approved.
Archive: Mengubah status dari Draft atau Approved ke Archived. Ini juga menonaktifkan Product terkait.
Set to Draft: Mengubah status dari Archived kembali ke Draft. Ini juga mengaktifkan kembali Product terkait.
🤝 Kontribusi
Kontribusi selalu diterima! Jika Anda memiliki ide perbaikan, menemukan bug, atau ingin menambahkan fitur baru, silakan:

Fork repositori ini.
Buat branch baru (git checkout -b feature/your-feature-name).
Lakukan perubahan dan commit (git commit -m 'feat: Add new feature').
Push ke branch Anda (git push origin feature/your-feature-name).
Buka Pull Request ke main branch repositori ini.
📄 Lisensi
Modul ini dirilis di bawah lisensi AGPL-3 (Affero General Public License, Version 3).

📞 Dukungan
Jika Anda memiliki pertanyaan, masalah, atau ingin berkonsultasi lebih lanjut, silakan buka issue di repositori ini.

# 📦 Material Management Integrated (Odoo 14)

## 🚀 Gambaran Umum Proyek

Modul **Material Management Integrated** adalah solusi komprehensif untuk mengelola material mentah (raw materials) dalam ekosistem Odoo 14 Anda. Berbeda dengan pendekatan tradisional yang hanya menggunakan modul Product bawaan, modul ini memperkenalkan model Material khusus yang terintegrasi secara cerdas dengan fungsionalitas Inventory (Stock) dan Purchases Odoo standar.

### Ini memungkinkan Anda untuk:

- Memiliki entitas khusus untuk material dengan atribut yang relevan.
- Secara otomatis mengelola produk terkait di modul Product Odoo.
- Melihat kuantitas stok Material secara real-time yang diambil dari data Inventory Odoo.
- Melacak riwayat pembelian Material berdasarkan Purchase Orders Odoo.
- Mengatur siklus hidup Material melalui workflow status yang jelas.

## ✨ Fitur Utama

- **Model Material Khusus**: Definisi Material dengan field unik seperti Material Code, Material Type (Fabric, Jeans, Cotton), Material Buy Price, Unit of Measure, Minimum Stock Quantity, dan Lifecycle Stage.

- **Integrasi Otomatis dengan Modul Odoo Standar**:
  - Setiap Material secara otomatis membuat dan terhubung ke satu Product.Product di modul Odoo Product bawaan.
  - Perubahan pada Material (nama, kode, harga, UoM) akan otomatis memperbarui Product terkait.
  - Manajemen stok dan pembelian material dilakukan sepenuhnya melalui modul Inventory dan Purchases Odoo standar.

- **Informasi Stok & Pembelian Real-time**:
  - **Current Stock Quantity**: Field terkomputasi yang menampilkan stok material saat ini, diambil langsung dari qty_available di Product.Product terkait.
  - **Last Purchase Date**: Field terkomputasi yang menunjukkan tanggal pembelian terakhir material, diambil dari Purchase Order Line terkait di Odoo.
  
- **Workflow Status Material**: Implementasi state (Draft, Approved, Archived) dengan button transisi di form view untuk mengelola siklus hidup material secara terkontrol.

- **Validasi Data Kuat**:
  - Validasi untuk Material Buy Price dan Material Code yang unik.
  - Validasi untuk memastikan setiap Material memiliki Product terkait yang unik.

- **Manajemen Supplier**: Default Supplier yang secara otomatis terhubung sebagai Vendor pada Product terkait.

- **Pengelolaan Otomatis Material Code**: Penomoran kode material secara otomatis saat pembuatan.

- **Pelacakan Komunikasi**: Integrasi mail.thread dan mail.activity.mixin untuk diskusi dan aktivitas pada setiap record Material.

## 🛠️ Instalasi

Untuk menginstal modul ini di Odoo 14 Anda:

1. Clone repositori ini ke dalam direktori addons Odoo Anda.

   ```bash
   git clone https://github.com/your_username/material_management_integrated.git /path/to/odoo/addons/material_registration
   ```

   (Ganti `/path/to/odoo/addons/material_registration` dengan jalur sebenarnya ke direktori addons Anda dan `your_username` dengan username GitHub Anda.)

2. Perbarui Daftar Aplikasi di Odoo.
3. Aktifkan Developer Mode.
4. Pergi ke **Apps** -> **Update Apps List**.
5. Cari dan Instal modul **"Material Management Integrated"**.

## 📖 Penggunaan

Setelah instalasi, Anda akan menemukan menu baru **"Material Management"** di Odoo Anda.

### Membuat Material Baru:

- Navigasi ke **Material Management** -> **Materials**.
- Klik **Create**.
- Isi detail material seperti Material Code (bisa otomatis), Material Name, Material Type, Material Buy Price, Default Supplier, dan Unit of Measure.
- Saat disimpan, sistem akan otomatis membuat Product terkait di modul Product Odoo.
- Anda bisa melihat Current Stock Quantity dan Last Purchase Date yang akan diperbarui secara otomatis berdasarkan transaksi Product terkait.

### Mengelola Stok Material:

- Stok material Anda dikelola melalui Product terkait di modul Inventory Odoo standar.
- Navigasi ke **Inventory** -> **Products** -> **Products**, cari material Anda (Anda bisa memfilter Is a Material Product).
- Lakukan penerimaan atau pengiriman stok seperti biasa melalui Inventory Adjustments, Receipts, dll. Current Stock Quantity pada record Material Anda akan diperbarui.

### Melakukan Pembelian Material:

- Pembelian material dilakukan melalui modul Purchases Odoo standar.
- Navigasi ke **Purchases** -> **Requests for Quotation**.
- Buat RFQ baru dan tambahkan Product material Anda ke Order Lines.
- Setelah Purchase Order dikonfirmasi, Last Purchase Date pada record Material Anda akan diperbarui.

### Mengubah Status Material:

Pada form view Material, gunakan button di bagian header:

- **Approve**: Mengubah status dari Draft ke Approved.
- **Archive**: Mengubah status dari Draft atau Approved ke Archived. Ini juga menonaktifkan Product terkait.
- **Set to Draft**: Mengubah status dari Archived kembali ke Draft. Ini juga mengaktifkan kembali Product terkait.

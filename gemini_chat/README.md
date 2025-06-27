# Modul Gemini Chat untuk Odoo 17

Modul ini mengintegrasikan Google Gemini AI ke dalam Odoo 17, memungkinkan Anda untuk berinteraksi dengan model bahasa Gemini langsung dari antarmuka Odoo.

## Fitur

- Chat dengan model Gemini Pro atau Gemini 1.5 Pro
- Riwayat percakapan yang tersimpan
- Antarmuka pengguna yang mudah digunakan
- Dukungan multi-pengguna

## Instalasi

1. Salin direktori `gemini_chat` ke direktori addons Odoo Anda
2. Install modul melalui Apps -> Update Apps List
3. Cari dan install modul "Gemini Chat"

## Konfigurasi

Sebelum menggunakan modul ini, Anda perlu mengatur parameter sistem berikut:

1. Buka Settings -> Technical -> Parameters -> System Parameters
2. Tambahkan parameter berikut:
   - `gemini.api.key`: API key Google Gemini Anda
   - `gemini.api.url` (opsional): URL endpoint API Gemini (default: https://generativelanguage.googleapis.com/v1beta/models/)

## Penggunaan

1. Buka menu Gemini Chat
2. Klik "Create" untuk membuat chat baru
3. Masukkan judul, pilih model, dan ketik pertanyaan Anda
4. Klik "Kirim ke Gemini" atau simpan untuk mengirim pertanyaan
5. Jawaban akan muncul di tab "Jawaban"

## Persyaratan

- Odoo 17.0 atau yang lebih baru
- Koneksi internet untuk mengakses API Gemini
- API key Google Gemini yang valid

## Lisensi

LGPL-3

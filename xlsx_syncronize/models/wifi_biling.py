from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)
import socket
import re
from dateutil.relativedelta import relativedelta
import os
from datetime import date, datetime
import gspread
from gspread.exceptions import WorksheetNotFound
from oauth2client.service_account import ServiceAccountCredentials

class WifiBilling(models.Model):
    _name = 'wifi.billing'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'WiFi Billing'

    partner_id = fields.Many2one('res.partner',string='Customer Name', required=True)
    phone = fields.Char(string='Phone Number')
    billing_date = fields.Date(string='Billing Date', default=fields.Date.today)
    amount = fields.Float(string='Amount')
    is_paid = fields.Boolean(string='Paid', default=False)
    partner_address = fields.Char(string='Alamat', readonly=True)
    # Field Selection Paket
    paket = fields.Selection(related='partner_id.default_package', string='Paket', store=True)
    sync_status = fields.Selection([
        ('not_synced', 'Not Synced'),
        ('pending', 'pending'),
        ('synced', 'Synced'),
        ('failed', 'Failed')
    ], string='Sync Status', default='not_synced')
    is_overdue = fields.Boolean(string='Overdue', compute='_compute_is_overdue', store=True)
    payment_status = fields.Selection([
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
        ('overdue', 'Overdue'),
    ], string="Payment Status", compute='_compute_payment_status', store=True)
    sequence_id = fields.Char(string="Sequence ID", readonly=True, copy=False, index=True)
    email = fields.Char(string='Email', related='partner_id.email')

    @api.onchange('is_paid')
    def _onchange_is_paid(self):
        if self.is_paid and self.sync_status != 'synced':
            self.sync_to_google_sheet()

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.phone = self.partner_id.phone
            self.partner_address = self.partner_id.street or self.partner_id.city
        else:
            self.phone = False
            self.partner_address = 'isi bos'

    @api.constrains('name', 'phone', 'billing_date')
    def _check_duplicate_billing(self):
        for record in self:
            bulan_ini = record.billing_date.strftime('%B %Y') if record.billing_date else ''
            existing = self.search([
                ('id', '!=', record.id),
                ('partner_id.name', '=', record.partner_id.name),
                ('phone', '=', record.phone),
                ('billing_date', '>=', record.billing_date.replace(day=1)),
                ('billing_date', '<', (record.billing_date.replace(day=1) + relativedelta(months=1))),
            ])
            if existing:
                raise ValidationError(
                    f"Customer '{record.partner_id.name}' dengan nomor {record.phone} sudah memiliki tagihan di bulan {bulan_ini}."
                )

    @api.onchange('paket')
    def _onchange_paket(self):
        paket_amount = {
            'paket_a': 100000,
            'paket_b': 150000,
            'paket_c': 200000,
        }
        self.amount = paket_amount.get(self.paket, 0.0)

    def sync_to_google_sheet(self):
        try:
            client = self._get_google_client()
            worksheet = self._get_worksheet(client)
            # Ensure headers and month column exist
            self._ensure_sheet_headers(worksheet)
            bulan = datetime.now().strftime('%B %Y')
            self._ensure_month_column(worksheet, bulan)
            # Find or create row for customer
            row_index = self._find_or_create_customer_row(worksheet)
            # if self._is_duplicate_entry(worksheet):
            #     raise ValidationError(
            #         f"Customer '{self.partner_id.name}' dengan nomor {self.phone} sudah melakukan pembayaran untuk bulan {bulan}.")
            headers = worksheet.row_values(1)
            if bulan not in headers:
                raise ValidationError(f"Kolom bulan '{bulan}' tidak ditemukan di header.")
            col_index = headers.index(bulan) + 1
            # Ensure row and column are within sheet limits
            max_rows = worksheet.row_count
            max_cols = worksheet.col_count
            if row_index > max_rows:
                worksheet.add_rows(row_index - max_rows)
                max_rows = worksheet.row_count
            if col_index > max_cols:
                worksheet.add_cols(col_index - max_cols)
                max_cols = worksheet.col_count
            value = 'Paid' if self.is_paid else 'Belum Bayar'
            worksheet.update_cell(row_index, col_index, value)
            self.sync_status = 'synced'
        except Exception as e:
            self.sync_status = 'pending'
            _logger.warning(f"Failed to sync to Google Sheet: {str(e)}")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('sequence_id'):
                vals['sequence_id'] = self.env['ir.sequence'].next_by_code('wifi.billing.seq') or '/'
        records = super().create(vals_list)
        for record in records:
            if record.partner_id and record.phone:
                record.partner_id.phone = record.phone
            if record.is_paid:
                record.sync_to_google_sheet()
        return records

    def _cron_retry_google_sync(self):
        print("kodingan ir cron ini di eksekusi")
        if self.is_internet_available():
            pending_records = self.search([('sync_status', '=', 'pending')])
            for record in pending_records:
                try:
                    record.sync_to_google_sheet()
                except Exception as e:
                    record.sync_status = 'failed'
                    _logger.error(f"Failed to sync to Google Sheet: {str(e)}")

    @staticmethod
    def is_internet_available():
        try:
            socket.create_connection(("www.google.com", 80))
            return True
        except OSError:
            return False

    def _get_or_create_worksheet(self, spreadsheet, sheet_name):
        try:
            return spreadsheet.worksheet(sheet_name)
        except WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows='1000',cols="20")
            worksheet.append_row(['Name', 'Phone', 'Paket', 'Amount', 'Status'])
            return worksheet

    def _sanitize_sheet_name(self, name):
        return re.sub(r'[\\/*?:[\]]', '_', name)[:100]

    @api.depends('partner_id', 'billing_date')
    def _compute_display_name(self):
        for record in self:
            customer = record.partner_id.name or ''
            bulan = record.billing_date.strftime('%B %Y') if record.billing_date else ''
            record.display_name = f"{customer} - {bulan}"

    def write(self, vals):
        res = super().write(vals)
        for record in self:
            if vals.get('is_paid') and record.is_paid:
                record.sync_to_google_sheet()
        return res

    def unlink(self):
        print("apakah ini menjadi salah satu hal")
        for rec in self:
            try:
                rec._delete_from_google_sheet()
            except Exception as e:
                print(f"Gagal hapus data dari Google Sheet untuk record {rec.partner_id.name}: {str(e)}")
                # Jangan raise UserError, supaya Odoo tetap lanjut hapus
                pass
        return super(WifiBilling, self).unlink()

    def action_confirm_delete(self):
        for rec in self:
            rec._delete_from_google_sheet()
            raise UserError("Data berhasil dihapus dari Google Sheet (tapi belum dari Odoo).")

    def _delete_from_google_sheet(self):
        client = self._get_google_client()
        worksheet = self._get_worksheet(client)
        row_index = self._find_row_index_in_sheet(worksheet)
        if row_index:
            worksheet.delete_rows(row_index)
        else:
            raise UserError("Data tidak ditemukan di Google Sheet.")

    def _find_row_index_in_sheet(self, worksheet):
        all_values = worksheet.get_all_values()
        for idx, row in enumerate(all_values, start=2):
            if row.get('ID') == self.sequence_id:
                worksheet.delete_rows(idx)
                return

    @api.depends('is_paid', 'billing_date')
    def _compute_is_overdue(self):
        today = date.today()
        for rec in self:
            if not rec.is_paid and rec.billing_date:
                is_late = rec.billing_date.replace(day=7) < today
                rec.is_overdue = is_late
            else:
                rec.is_overdue = False

    @api.depends('is_paid', 'is_overdue')
    def _compute_payment_status(self):
        for rec in self:
            if rec.is_paid:
                rec.payment_status = 'paid'
            elif rec.is_overdue:
                rec.payment_status = 'overdue'
            else:
                rec.payment_status = 'unpaid'

    def _get_google_client(self):
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive',
        ]
        creds_path = os.path.join(os.path.dirname(__file__), '..','config', 'odoo_spreedsheet.json')
        creds_path = os.path.abspath(creds_path)
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        print(creds)
        return gspread.authorize(creds)

    def _get_worksheet(self, client):
        sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1Tb4MzYw6f2wpSWTbi5m8gIFBxBfF4Ir9PYhrZ-JuxgQ/edit?usp=sharing")
        alamat = self.partner_id.street or 'Default'
        sheet_name = self._sanitize_sheet_name(alamat)
        return self._get_or_create_worksheet(sheet,sheet_name)

    def _ensure_sheet_headers(self, worksheet):
        expected_header = ['ID','Customer Name', 'Phone', 'Email','Tanggal Bayar', 'Amount', 'Status', 'Bulan']
        current_headers = worksheet.row_values(1)
        if current_headers != expected_header:
            worksheet.delete_rows(1)
            worksheet.insert_row(expected_header, 1)

    def _prepare_row_data(self):
        bulan = datetime.now().strftime("%B %Y")
        tanggal = str(self.billing_date or fields.Date.today())
        amount = str(self.amount or "0")
        status = 'Paid' if self.is_paid else 'Belum Bayar'
        print(bulan, tanggal,amount,status)
        return [self.sequence_id,self.partner_id.name, self.phone, self.email, tanggal, amount, status, bulan]

    def _is_duplicate_entry(self, worksheet):
        bulan = datetime.now().strftime('%B %Y')
        all_records = worksheet.get_all_records()
        for record in all_records:
            if (
                record.get('Customer Name') == self.partner_id.name and
                record.get('Phone') == self.phone and
                record.get('Bulan') == bulan
            ):
                return True
        return False

    def _ensure_month_column(self, worksheet, bulan):
        headers = worksheet.row_values(1)
        if bulan not in headers:
            worksheet.update_cell(1, len(headers) + 1, bulan)

    def _find_or_create_customer_row(self, worksheet):
        all_records = worksheet.get_all_records()
        for idx, record in enumerate(all_records, start=2):  # Mulai dari baris ke-2
            if record.get('Customer Name') == self.partner_id.name and record.get('Phone') == self.phone:
                return idx  # Return row number
        # If not found, append row and return its index
        worksheet.append_row(self._prepare_row_data())
        # After append, get the actual last row with data
        all_records = worksheet.get_all_records()
        return len(all_records) + 1

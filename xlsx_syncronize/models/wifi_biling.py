from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import requests
import os
from datetime import date, datetime
import gspread
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
    sync_status = fields.Selection([
        ('not_synced', 'Not Synced'),
        ('synced', 'Synced')
    ], string='Sync Status', default='not_synced')
    is_overdue = fields.Boolean(string='Overdue', compute='_compute_is_overdue', store=True)
    payment_status = fields.Selection([
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
        ('overdue', 'Overdue'),
    ], string="Payment Status", compute='_compute_payment_status', store=True)

    @api.onchange('is_paid')
    def _onchange_is_paid(self):
        if self.is_paid and self.sync_status != 'synced':
            self.sync_to_google_sheet()

    def sync_to_google_sheet(self):
        client = self._get_google_client()
        worksheet = self._get_worksheet(client)
        # Ensure headers and month column exist
        self._ensure_sheet_headers(worksheet)
        bulan = datetime.now().strftime('%B %Y')
        self._ensure_month_column(worksheet, bulan)
        # Find or create row for customer
        row_index = self._find_or_create_customer_row(worksheet)
        if self._is_duplicate_entry(worksheet):
            raise ValidationError(
                f"Customer '{self.partner_id.name}' dengan nomor {self.phone} sudah melakukan pembayaran untuk bulan {bulan}.")
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

    @api.model
    def create(self, vals):
        records = super().create(vals)
        for record in records:
            if record.is_paid:
                record.sync_to_google_sheet()
        return records

    def write(self, vals):
        res = super().write(vals)
        for record in self:
            if vals.get('is_paid') and record.is_paid:
                record.sync_to_google_sheet()
        return res

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
        return sheet.sheet1

    def _ensure_sheet_headers(self, worksheet):
        expected_header = ['Customer Name', 'Phone', 'Tanggal Bayar', 'Amount', 'Status', 'Bulan']
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
        return [self.partner_id.name, self.phone, tanggal, amount, status, bulan]

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

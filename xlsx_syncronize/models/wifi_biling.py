from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import requests
from datetime import date, datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class WifiBilling(models.Model):
    _name = 'wifi.billing'
    _description = 'WiFi Billing'

    name = fields.Char(string='Customer Name', required=True)
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
        url = "https://script.google.com/macros/s/AKfycbwPfmAAvwJsVXmw1DmNzBvo5URkeI9-SWuseYKBQlApgD7N0b9cs9tMcl9984sbtZ85/exec"
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("/Users/farhan/odoo_custom/odoo18/xlsx_syncronize/models/odoo_spreedsheet.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1Tb4MzYw6f2wpSWTbi5m8gIFBxBfF4Ir9PYhrZ-JuxgQ/edit?usp=sharing")
        worksheet = sheet.sheet1
        all_records = worksheet.get_all_records()
        print(all_records)
        billing_month = self.billing_date.strftime('%Y-%m')
        for record in all_records:
            record_month = datetime.strptime(record['Billing Date'], '%Y-%m-%d').strftime('%Y-%m')
            if (record['Customer Name'] == self.name and record['Phone'] == self.phone and record_month == billing_month):
                raise UserError("Customer ini sudah bayar di bulan yang sama, statusnya sudah paid!")
        # Jika aman, tambahkan ke sheet
        worksheet.append_row([
            self.name,
            self.phone,
            self.amount,
            self.billing_date.strftime('%Y-%m-%d'),
            'Paid'
        ])

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



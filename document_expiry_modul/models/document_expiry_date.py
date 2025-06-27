from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, timedelta

class DocumentExpiry(models.Model):
    _name = 'document.expiry'
    _description = "Document Expiry"

    name = fields.Char(string="Document Name", required=True)
    partner_id = fields.Many2one('res.partner', string='Owner')
    document_type = fields.Selection([
        ('iso', 'ISO Certification'),
        ('siup', 'SIUP'),
        ('tdp', 'TDP'),
        ('nib', 'NIB'),
        ('akta', 'Akta'),
        ('other', 'Other')
    ], string='Document Type', required=True)
    issue_date = fields.Date(string='Issue Date')
    expiry_date = fields.Date(string='Expiry Date', required=True)
    attachment_id = fields.Many2one('ir.attachment', string='Document File')
    state = fields.Selection([
        ('valid', 'Valid'),
        ('nearly_expired', 'Nearly Expired'),
        ('expired', 'Expired')
    ], string='Status', default='valid', readonly=True)
    notification_sent = fields.Boolean(string='Notification Sent', default=False)

    @api.constrains('expiry_date')
    def _check_expiry_date(self):
        for rec in self:
            if rec.expiry_date < fields.Date.today():
                raise ValidationError("Expiry date must be greater than or equal to today's date.")

    @api.model
    def _cron_check_expiry(self):
        today = fields.Date.today()
        warn_date = today + timedelta(days=14)

        docs = self.search([])
        for doc in docs:
            previous_state = doc.state
            if doc.expiry_date < today:
                doc.state = "expired"
            elif today <= doc.expiry_date <= warn_date:
                doc.state = "nearly_expired"
            else:
                doc.state = "valid"
            if previous_state != doc.state:
                doc.notification_sent = False

class DocumentExpiryLog(models.Model):
    _name = 'document.expiry.log'
    _description = 'Log History of Document Status Changes'
    _order = 'changed_on desc'

    document_id = fields.Many2one('document.expiry', string='Document', required=True, ondelete='cascade')
    previous_state = fields.Selection([
        ('valid', 'Valid'),
        ('nearly_expired', 'Nearly Expired'),
        ('expired', 'Expired')
    ], string='Previous Status', required=True)
    new_state = fields.Selection([
        ('valid', 'Valid'),
        ('nearly_expired', 'Nearly Expired'),
        ('expired', 'Expired')
    ], string='New Status', required=True)
    changed_on = fields.Datetime(string='Changed On', default=fields.Datetime.now)
    changed_by = fields.Many2one('res.users', string='Changed By', default=lambda self: self.env.uid)

    @api.model
    def _cron_check_expiry(self):
        today = fields.Date.today()
        warn_date = today + timedelta(days=14)
        docs = self.search([])
        for doc in docs:
            previous_state = doc.state
            
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class CrmSlaPolicy(models.Model):
    _name = 'crm.sla.policy'
    _description = 'SLA Policy'
    _order = 'company_id, team_id, stage_id'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', default= lambda self: self.env.company, required=True)
    team_id = fields.Many2one('crm.team', string='Team', required=True)
    stage_id = fields.Many2one('crm.stage', string='Stage', required=True)
    sla_hours = fields.Integer(string='SLA Hours', required=True, default=24,help='Max hours without a planned activity / follow-up before considered overdue.')
    warn_hours = fields.Integer(string='Warn After Hours', default=12,help='Warn earlier than SLA to create a warning activity.')
    activity_type_id = fields.Many2one('mail.activity.type', string='Activity Type',help='Activity type to schedule when SLA is near/breached.')

    @api.constrains('sla_hours', 'warn_hours')
    def _check_sla_hours(self):
        for rec in self:
            if rec.sla_hours <= 0:
                raise ValidationError(_('SLA Hours must be greater than 0.'))
            if rec.warn_hours < 0:
                raise ValidationError(_('Warn After Hours must be greater than or equal to 0.'))
            if rec.warn_hours > rec.sla_hours:
                raise ValidationError(_('Warn After Hours must be less than or equal to SLA Hours.'))


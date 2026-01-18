from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class CrmLeadAssignmentRule(models.Model):
    _name = 'crm.lead.assignment.rule'
    _description = 'CRM Lead Assignment Rule'
    _order = 'sequence, id'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    team_id = fields.Many2one('crm.team', string='Sales Team', required=True)
    source_id = fields.Many2one('utm.source', string='Source')
    country_id = fields.Many2one('res.country', string='Country')
    tag_id = fields.Many2one('crm.tag', string='Tag')
    assignment_mode = fields.Selection([
        ('round_robin', 'Round Robin'),
        ('fixed', 'Fixed User'),
    ], default='round_robin', required=True)
    fixed_user_id = fields.Many2one('res.users', string='Fixed User')
    max_open_leads = fields.Integer(default=50,help='Do not assign to a user if they exceed this number of open leads.')

    @api.constrains('assignment_mode', 'fixed_user_id')
    def _check_assignment_mode(self):
        for rec in self:
            if rec.assignment_mode == 'fixed' and not rec.fixed_user_id:
                raise ValidationError(_('Fixed User is required when assignment mode is Fixed User.'))

class CrmTeam(models.Model):
    _inherit = 'crm.team'

    rr_index = fields.Integer(default=0, help='Round-robin pointer (training).')


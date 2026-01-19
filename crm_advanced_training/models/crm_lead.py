from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    bant_budget = fields.Selection([
        ('unknown', 'Unknown'),
        ('low', 'Low'),
        ('mid', 'Medium'),
        ('high', 'High'),
    ], default='unknown', tracking=True)
    bant_authority = fields.Selection([
        ('unknown', 'Unknown'),
        ('influencer', 'Influencer'),
        ('decision_maker', 'Decision Maker'),
    ], default='unknown', tracking=True)
    bant_need = fields.Selection([
        ('unknown', 'Unknown'),
        ('nice', 'Nice to have'),
        ('must', 'Must have'),
    ], default='unknown', tracking=True)
    bant_timeline = fields.Selection([
        ('unknown', 'Unknown'),
        ('this_month', 'This month'),
        ('this_quarter', 'This quarter'),
        ('later', 'Later'),
    ], default='unknown', tracking=True)
    qualification_note = fields.Text(tracking=True)
    is_qualified = fields.Boolean(compute='_compute_is_qualified', store=True)
    sla_deadline = fields.Datetime(compute='_compute_sla', store=True)
    sla_warn_deadline = fields.Datetime(compute='_compute_sla', store=True)
    sla_breached = fields.Boolean(compute='_compute_sla', store=True)
    x_lead_score = fields.Integer(string='Custom Lead Score', compute='_compute_custom_score', store=True)
    x_score_breakdown = fields.Text(string='Score Breakdown', compute='_compute_custom_score', store=True)
    x_is_hot = fields.Boolean(compute='_compute_hot', store=True)

    @api.depends('bant_budget', 'bant_authority', 'bant_need', 'bant_timeline')
    def _compute_is_qualified(self):
        for lead in self:
            lead.is_qualified = all([
                lead.bant_budget != 'unknown',
                lead.bant_authority != 'unknown',
                lead.bant_need != 'unknown',
                lead.bant_timeline != 'unknown',
            ])

    @api.depends('x_lead_score')
    def _compute_hot(self):
        for lead in self:
            lead.x_is_hot = lead.x_lead_score >= 80

    @api.depends('source_id', 'country_id', 'bant_budget', 'bant_need', 'bant_timeline', 'partner_id', 'email_from')
    def _compute_custom_score(self):
        for lead in self:
            score = 0
            parts = []

            if lead.source_id:
                score += 10
                parts.append('source:+10')

            if lead.country_id:
                score += 5
                parts.append('country:+5')
            if lead.email_from and '@' in lead.email_from:
                domain = lead.email_from.split('@')[-1].lower().strip()
                if domain in ('gmail.com', 'outlook.com', 'yahoo.com'):
                    score += 5
                    parts.append('public_email:+5')
                else:
                    score += 5
                    parts.append('company_email:+10')
                    # BANT
                    if lead.bant_budget == 'high':
                        score += 25
                        parts.append('budget(high):+25')
                    elif lead.bant_budget == 'mid':
                        score += 15
                        parts.append('budget(mid):+15')

                    if lead.bant_need == 'must':
                        score += 20
                        parts.append('need(must):+20')
                    elif lead.bant_need == 'nice':
                        score += 10
                        parts.append('need(nice):+10')

                    if lead.bant_timeline == 'this_month':
                        score += 20
                        parts.append('timeline(this_month):+20')
                    elif lead.bant_timeline == 'this_quarter':
                        score += 10
                        parts.append('timeline(this_quarter):+10')

                    # Partner linked (opportunity quality)
                    if lead.partner_id:
                        score += 10
                        parts.append('partner_linked:+10')

                    lead.x_lead_score = min(score, 100)
                    lead.x_score_breakdown = ', '.join(parts) if parts else 'no signals'

    @api.depends('team_id', 'stage_id', 'activity_ids.date_deadline', 'write_date', 'create_date')
    def _compute_sla(self):
        Policy = self.env['crm.sla.policy']
        for lead in self:
            lead.sla_deadline = False
            lead.sla_warn_deadline = False
            lead.sla_breached = False
            if not lead.team_id or not lead.stage_id:
                continue
            policy = Policy.search([
                ('active', '=', True),
                ('company_id', '=', lead.company_id.id),
                ('team_id', '=', lead.team_id.id),
                ('stage_id', '=', lead.stage_id.id),
            ], limit=1)
            if not policy:
                continue
            baseline = lead.write_date or lead.create_date

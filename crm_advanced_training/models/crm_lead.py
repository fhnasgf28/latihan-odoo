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

    # -----------------
    # SLA
    # -----------------
    sla_deadline = fields.Datetime(compute='_compute_sla', store=True)
    sla_warn_deadline = fields.Datetime(compute='_compute_sla', store=True)
    sla_breached = fields.Boolean(compute='_compute_sla', store=True)

    # -----------------
    # Custom scoring (latihan)
    # -----------------
    x_lead_score = fields.Integer(string='Custom Lead Score', compute='_compute_custom_score', store=True)
    x_score_breakdown = fields.Text(string='Score Breakdown', compute='_compute_custom_score', store=True)

    # helper for UI badges
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

    # @api.depends('source_id', 'country_id', 'bant_budget')
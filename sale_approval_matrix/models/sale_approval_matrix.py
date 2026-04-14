from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleApprovalMatrix(models.Model):
    _name = 'sale.approval.matrix'
    _description = 'Sales Order Approval Matrix'
    _order = 'sequence, amount_min, id'

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    amount_min = fields.Monetary(string="Minimum Amount", required=True)
    amount_max = fields.Monetary(string="Maximum Amount", required=True)
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        related='company_id.currency_id',
        store=True,
        readonly=True,
    )
    approver_ids = fields.Many2many(
        'res.users',
        string="Approvers",
        required=True,
        help="Users who can approve SO in this range.",
    )
    minimum_approval_count = fields.Integer(
        string="Minimum Approvals Required",
        default=1,
        required=True,
        help="Minimal jumlah approver yang harus approve sebelum SO bisa terkonfirmasi.",
    )

    _sql_constraints = [
        (
            'check_amount_range',
            'CHECK(amount_max >= amount_min)',
            'Maximum amount must be greater than or equal to minimum amount.',
        ),
        (
            'check_minimum_approval_count',
            'CHECK(minimum_approval_count > 0)',
            'Minimum approval count must be greater than 0.',
        ),
    ]

    @api.constrains('approver_ids', 'minimum_approval_count')
    def _check_minimum_approval_count(self):
        for rec in self:
            if rec.minimum_approval_count > len(rec.approver_ids):
                raise ValidationError(
                    _("Minimum approvals cannot be greater than approver count.")
                )

    @api.constrains('amount_min', 'amount_max', 'company_id', 'active')
    def _check_overlap_ranges(self):
        for rec in self.filtered(lambda r: r.active):
            domain = [
                ('id', '!=', rec.id),
                ('company_id', '=', rec.company_id.id),
                ('active', '=', True),
                ('amount_min', '<=', rec.amount_max),
                ('amount_max', '>=', rec.amount_min),
            ]
            overlap = self.search_count(domain)
            if overlap:
                raise ValidationError(
                    _(
                        "Amount range overlaps with another active rule in company %s."
                    )
                    % rec.company_id.display_name
                )

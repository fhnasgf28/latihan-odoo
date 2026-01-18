from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class RentalApprovalMatrix(models.Model):
    _name = 'rental.approval.matrix'
    _description = 'Rental Approval Matrix'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True)
    rule_type = fields.Selection([
        ('by_amount', 'By Amount'),
        ('simple', 'Simple')
    ], default='simple', required=True, tracking=True)
    line_ids = fields.One2many('rental.approval.matrix.line', 'matrix_id', string='Steps', copy=True)

    @api.constrains('line_ids')
    def _check_steps(self):
        for rec in self:
            if not rec.line_ids:
                raise ValidationError(_('Please add at least one step'))

class ApprovalMatrixLine(models.Model):
    _name = 'rental.approval.matrix.line'
    _description = 'Rental Approval Matrix Line'

    matrix_id = fields.Many2one('rental.approval.matrix', string='Matrix', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)
    user_id = fields.Many2one('res.users', string='Approver User', required=True)
    group_id = fields.Many2one('res.group', string='Approver Group')
    min_amount = fields.Monetary(string='Min Amount', default=0.0)
    max_amount = fields.Monetary(string='Max Amount', default=0.0)
    currency_id = fields.Many2one('res.currency', string='Currency', related='matrix_id.company_id.currency_id', readonly=True)

    @api.constrains('user_id', 'group_id')
    def _check_user_group(self):
        for rec in self:
            if bool(rec.user_id) == bool(rec.group_id):
                raise ValidationError(_('Please select either user or group'))

class RentalApprovalStep(models.Model):
    _name = 'rental.approval.step'
    _description = 'Rental Approval Step'

    order_id = fields.Many2one('rental.order', string='Order', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)
    user_id = fields.Many2one('res.users', string='Approver User', required=True)
    group_id = fields.Many2one('res.group', string='Approver Group')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('skipped', 'Skipped')
    ], default='pending', required=True, tracking=True)
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True)
    approved_date = fields.Datetime(string='Approved Date', readonly=True)
    noted = fields.Char(string='Note')

    def _is_user_allowed(self, user=None):
        user = user or self.env.user
        self.ensure_one()
        if self.user_id:
            return user == self.user_id
        if self.group_id:
            return self.group_id in user.groups_id
        return False
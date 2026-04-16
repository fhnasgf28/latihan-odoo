from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResUsersDelegation(models.Model):
    _name = 'res.users.delegation'
    _description = 'Approver Delegation'
    _order = 'date_start desc'

    delegator_id = fields.Many2one(
        'res.users', 
        string="Delegator", 
        required=True, 
        default=lambda self: self.env.user,
        help="User who is delegating their authority."
    )
    delegate_id = fields.Many2one(
        'res.users', 
        string="Delegate", 
        required=True,
        help="User who will receive the authority."
    )
    date_start = fields.Date(string="Start Date", required=True)
    date_end = fields.Date(string="End Date", required=True)
    reason = fields.Text(string="Reason/Description", help="Reason for this delegation (e.g. Annual Leave, Business Trip)")
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('check_dates', 'CHECK(date_end >= date_start)', 'End date must be after start date.'),
    ]

    @api.constrains('delegator_id', 'delegate_id')
    def _check_self_delegation(self):
        for rec in self:
            if rec.delegator_id == rec.delegate_id:
                raise ValidationError(_("You cannot delegate to yourself."))

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, _("%s to %s") % (rec.delegator_id.name, rec.delegate_id.name)))
        return res

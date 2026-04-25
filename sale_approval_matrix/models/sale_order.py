from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(selection_add=[
        ('to_approve', 'To Approve'),
        ('rejected', 'Rejected')
    ], ondelete={'to_approve': 'set default', 'rejected': 'set default'})

    approval_matrix_id = fields.Many2one('sale.approval.matrix', string="Approval Matrix Rule", readonly=True, copy=False)
    approver_ids = fields.Many2many('res.users', related='approval_matrix_id.approver_ids', string="Wait For Approvers", readonly=True)
    minimum_approval_count = fields.Integer(related='approval_matrix_id.minimum_approval_count', readonly=True)
    approved_user_ids = fields.Many2many(
        'res.users',
        'sale_order_approved_user_rel',
        'order_id',
        'user_id',
        string="Approved Users",
        copy=False,
        readonly=True,
    )
    pending_approver_ids = fields.Many2many(
        'res.users',
        compute='_compute_pending_approver_ids',
        search='_search_pending_approver_ids',
        string="Pending Approvers",
        readonly=True,
    )

    def _search_pending_approver_ids(self, operator, value):
        if operator not in ('in', '=', 'not in', '!='):
            return []
        
        # If value is a list, take the first one (usually uid)
        user_id = value[0] if isinstance(value, list) else value
        
        # 1. Direct approvers
        direct_domain = [('approver_ids', operator, user_id), ('approved_user_ids', 'not in', [user_id])]
        
        # 2. Delegated approvers
        today = fields.Date.today()
        delegations = self.env['res.users.delegation'].search([
            ('delegate_id', '=', user_id),
            ('date_start', '<=', today),
            ('date_end', '>=', today),
            ('active', '=', True)
        ])
        delegator_ids = delegations.mapped('delegator_id').ids
        
        if delegator_ids:
            # Match if any pending approver is a delegator for the current user
            delegated_domain = [('approver_ids', 'in', delegator_ids), ('approved_user_ids', 'not in', delegator_ids)]
            return ['|'] + direct_domain + delegated_domain
        
        return direct_domain
    approval_count = fields.Integer(
        compute='_compute_approval_count',
        string='Approval Count',
        readonly=True,
    )

    can_approve = fields.Boolean(
        compute='_compute_can_approve',
        string="Can Approve",
        help="Check if current user can approve/reject this SO."
    )

    is_approved = fields.Boolean(string="Is Approved", default=False, copy=False)
    approved_by_id = fields.Many2one('res.users', string="Approved By", readonly=True, copy=False)
    approval_date = fields.Datetime(string="Approval Date", readonly=True, copy=False)
    rejection_reason = fields.Text(string="Rejection Reason", readonly=True, copy=False)

    @api.depends('approver_ids', 'approved_user_ids')
    def _compute_can_approve(self):
        today = fields.Date.today()
        for order in self:
            # Check if user is an original approver
            is_original_approver = self.env.user in order.approver_ids and self.env.user not in order.approved_user_ids
            
            # Check if user is a delegate for a pending approver
            delegator_ids = self.env['res.users.delegation'].search([
                ('delegate_id', '=', self.env.user.id),
                ('date_start', '<=', today),
                ('date_end', '>=', today),
                ('active', '=', True)
            ]).mapped('delegator_id')
            
            is_delegate = any(d in order.pending_approver_ids for d in delegator_ids)
            
            order.can_approve = is_original_approver or is_delegate

    @api.depends('approved_user_ids')
    def _compute_approval_count(self):
        for order in self:
            order.approval_count = len(order.approved_user_ids)

    @api.depends('approver_ids', 'approved_user_ids')
    def _compute_pending_approver_ids(self):
        for order in self:
            order.pending_approver_ids = order.approver_ids - order.approved_user_ids

    def _get_matching_approval_rule(self):
        self.ensure_one()
        return self.env['sale.approval.matrix'].search([
            ('company_id', '=', self.company_id.id),
            ('active', '=', True),
            ('amount_min', '<=', self.amount_total),
            ('amount_max', '>=', self.amount_total),
        ], order='sequence, amount_min, id', limit=1)

    def _check_approval_permission(self):
        self.ensure_one()
        if self.env.user in self.approval_matrix_id.approver_ids:
            return True
        
        # Check if user is a delegate
        today = fields.Date.today()
        delegation = self.env['res.users.delegation'].search([
            ('delegate_id', '=', self.env.user.id),
            ('date_start', '<=', today),
            ('date_end', '>=', today),
            ('active', '=', True),
            ('delegator_id', 'in', self.pending_approver_ids.ids)
        ], limit=1)
        
        if delegation:
            return True
        return False

    def action_confirm(self):
        """
        Check if the Sales Order needs approval based on the Matrix.
        """
        if self.env.context.get('skip_sale_approval_matrix'):
            return super(SaleOrder, self).action_confirm()

        orders_for_standard_confirm = self.browse()
        for order in self:
            if order.state not in ('draft', 'sent'):
                continue

            if order.is_approved:
                orders_for_standard_confirm |= order
                continue

            matrix_rule = order._get_matching_approval_rule()

            if matrix_rule:
                order.write({
                    'state': 'to_approve',
                    'approval_matrix_id': matrix_rule.id,
                    'approved_user_ids': [(5, 0, 0)],
                })
                msg = _("This order requires approval from: %s") % ", ".join(matrix_rule.approver_ids.mapped('name'))
                order.message_post(body=msg)
            else:
                orders_for_standard_confirm |= order

        if orders_for_standard_confirm:
            return super(SaleOrder, orders_for_standard_confirm).action_confirm()
        return True

    def action_approve(self):
        """
        Check if current user is in the list of authorized approvers for this order.
        """
        for order in self:
            if order.state != 'to_approve':
                continue

            if not order.approval_matrix_id:
                raise UserError(_("Approval matrix is missing on this order. Please reset approval first."))

            if not order._check_approval_permission():
                raise UserError(_("You are not authorized to approve this Sales Order. Authorized users: %s") % 
                                ", ".join(order.approval_matrix_id.approver_ids.mapped('name')))

            if self.env.user in order.approved_user_ids:
                raise UserError(_("You have already approved this Sales Order."))

            # Check if current user is a delegate
            today = fields.Date.today()
            delegation = self.env['res.users.delegation'].search([
                ('delegate_id', '=', self.env.user.id),
                ('date_start', '<=', today),
                ('date_end', '>=', today),
                ('active', '=', True),
                ('delegator_id', 'in', order.pending_approver_ids.ids)
            ], limit=1)

            order.write({
                'approved_user_ids': [(4, self.env.user.id)]
            })

            if delegation:
                msg = _("%s approved this Sales Order on behalf of %s.") % (
                    self.env.user.display_name, 
                    delegation.delegator_id.display_name
                )
                if delegation.reason:
                    msg += _("<br/>Reason: %s") % delegation.reason
            else:
                msg = _("%s approved this Sales Order.") % self.env.user.display_name
            
            order.message_post(body=msg)

            if len(order.approved_user_ids) < order.minimum_approval_count:
                remaining = order.minimum_approval_count - len(order.approved_user_ids)
                order.message_post(
                    body=_(
                        "Approval progress: %s/%s. Still need %s approval(s)."
                    ) % (len(order.approved_user_ids), order.minimum_approval_count, remaining)
                )
                continue

            order.write({
                'is_approved': True,
                'approved_by_id': self.env.user.id,
                'approval_date': fields.Datetime.now(),
                'state': 'draft',
            })
            super(SaleOrder, order.with_context(skip_sale_approval_matrix=True)).action_confirm()
        return True

    def action_reject(self):
        self.ensure_one()
        if self.state != 'to_approve':
            raise UserError(_("You can only reject orders that are waiting for approval."))
        
        if not self._check_approval_permission():
            raise UserError(_("You are not authorized to reject this Sales Order."))

        return {
            'name': _('Provide Rejection Reason'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.rejection.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id},
        }

    def _perform_rejection(self):
        for order in self:
            if order.state != 'to_approve':
                continue
            
            # Re-verify permissions for safety
            if not order._check_approval_permission():
                raise UserError(_("You are not authorized to reject this Sales Order."))
            
            reason = self.env.context.get('rejection_reason', _('No reason provided.'))
            
            # Check if current user is a delegate
            today = fields.Date.today()
            delegation = self.env['res.users.delegation'].search([
                ('delegate_id', '=', self.env.user.id),
                ('date_start', '<=', today),
                ('date_end', '>=', today),
                ('active', '=', True),
                ('delegator_id', 'in', order.pending_approver_ids.ids)
            ], limit=1)

            order.write({
                'state': 'rejected',
                'is_approved': False,
                'approval_date': False,
                'approved_by_id': False,
                'approved_user_ids': [(5, 0, 0)],
                'rejection_reason': reason,
            })
            
            if delegation:
                msg = _("<b>Sales Order Rejected.</b><br/><b>Rejected by:</b> %s (on behalf of %s)<br/><b>Reason:</b> %s") % (
                    self.env.user.display_name,
                    delegation.delegator_id.display_name,
                    reason
                )
            else:
                msg = _("<b>Sales Order Rejected.</b><br/><b>Rejected by:</b> %s<br/><b>Reason:</b> %s") % (
                    self.env.user.display_name,
                    reason
                )
            order.message_post(body=msg)
        return True

    def action_draft(self):
        res = super(SaleOrder, self).action_draft()
        for order in self:
            order.write({
                'is_approved': False,
                'approval_date': False,
                'approved_by_id': False,
                'approved_user_ids': [(5, 0, 0)],
                'approval_matrix_id': False,
                'rejection_reason': False,
            })
        return res

    def action_reset_approval(self):
        for order in self:
            order.write({
                'state': 'draft',
                'approval_matrix_id': False,
                'is_approved': False,
                'approval_date': False,
                'approved_by_id': False,
                'approved_user_ids': [(5, 0, 0)],
            })
            order.message_post(body=_("Approval flow has been reset."))
        return True

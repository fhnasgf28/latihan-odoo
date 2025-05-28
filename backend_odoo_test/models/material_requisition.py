from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class MaterialRequisition(models.Model):
    _name = 'material.requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Internal Material Requisition'
    _order = 'request_date desc, id desc'

    name = fields.Char(string='Requisition Reference', required=True, copy=False, readonly=True,states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    request_date = fields.Datetime(string='Request Date', required=True, default=fields.Datetime.now, readonly=True,states={'draft': [('readonly', False)]})
    requested_by = fields.Many2one('res.users', string='Requested By', required=True,default=lambda self: self.env.user,readonly=True, states={'draft': [('readonly', False)]})
    department_id = fields.Many2one('hr.department', string='Department', readonly=True,states={'draft': [('readonly', False)]},help="Department requesting the materials.")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', readonly=True, tracking=True)
    line_ids = fields.One2many('material.material.order.line', 'requisition_id', string='Requisition Lines',readonly=True, states={'draft': [('readonly', False)]})
    notes = fields.Text(string='Internal Notes')

    def action_submit_for_approval(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_("You cannot submit a requisition without any material lines."))
            rec.write({'state': 'to_approve'})
            rec.message_post(body=_("Material Requisition submitted for approval."))

    def action_approve(self):
        for rec in self:
            if rec.state != 'to_approve':
                raise UserError(_("Material Requisition can only be approved from 'To Approve' state."))
            rec.write({'state': 'approved'})
            rec.message_post(body=_("Material Requisition approved."))

    def action_transfer_materials(self):
        """
        This method would typically create stock moves/transfers in Odoo's stock module.
        For this example, it just moves to 'Done'.
        """
        for rec in self:
            if rec.state != 'approved':
                raise UserError(_("Materials can only be transferred for 'Approved' requisitions."))
            # TODO: Implement actual stock transfer logic here,
            # e.g., create stock.picking records based on material_id.product_id

            # Example: Check if all requested quantity is available
            for line in rec.line_ids:
                if line.quantity > line.available_quantity:
                    raise UserError(
                        _("Not enough stock for material '%s'. Requested: %s, Available: %s") % (line.material_id.name,
                                                                                                 line.quantity,
                                                                                                 line.available_quantity))
            rec.write({'state': 'done'})
            rec.message_post(body=_("Materials transferred and requisition marked as Done."))

    def action_cancel(self):
        for rec in self:
            if rec.state not in ['draft', 'to_approve']:
                raise UserError(_("Material Requisition cannot be cancelled from current state."))
            rec.write({'state': 'cancel'})
            rec.message_post(body=_("Material Requisition cancelled."))

    def action_set_to_draft(self):
        for rec in self:
            if rec.state == 'cancel':
                rec.write({'state': 'draft'})
                rec.message_post(body=_("Material Requisition reset to Draft."))
            else:
                raise UserError(_("Material Requisition can only be reset to Draft from 'Cancelled' state."))

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('material.requisition') or _('New')
        return super(MaterialRequisition, self).create(vals)
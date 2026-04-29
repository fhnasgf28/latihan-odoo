from odoo import models, fields, api, _

class SaleOrderRejectionWizard(models.TransientModel):
    _name = 'sale.order.rejection.wizard'
    _description = 'Sale Order Rejection Wizard'

    order_id = fields.Many2one('sale.order', string="Sales Order", required=True, readonly=True)
    reason = fields.Text(string="Reason for Rejection", required=True)

    def action_reject_confirm(self):
        self.ensure_one()
        # Actual rejection logic is called here
        self.order_id.with_context(rejection_reason=self.reason)._perform_rejection()
        return {'type': 'ir.actions.act_window_close'}

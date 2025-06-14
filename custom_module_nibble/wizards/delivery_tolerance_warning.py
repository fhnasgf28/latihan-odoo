from odoo import models, fields, api, _

class DeliveryToleranceWarning(models.TransientModel):
    _name = 'delivery.tolerance.warning'
    _description = 'Delivery Tolerance Warning'

    picking_id = fields.Many2one('stock.picking', string='Picking')
    warning_message = fields.Html(string='Warning Message', readonly=True)

    def action_confirm(self):
        """Confirm and proceed with validation despite exceeding tolerance"""
        if self.picking_id:
            return self.picking_id.with_context(bypass_tolerance_warning=True).button_validate()
        return {'type': 'ir.actions.act_window_close'}
    
    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}

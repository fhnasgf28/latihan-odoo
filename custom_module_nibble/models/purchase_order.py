from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        res = super().button_confirm()
        for order in self:
            for picking in order.picking_ids:
                picking.partner_ref = order.partner_ref
        return res

    def write(self, vals):
        res = super().write(vals)
        if 'partner_ref' in vals:
            for order in self:
                for picking in order.picking_ids:
                    picking.partner_ref = vals['partner_ref']
        return res
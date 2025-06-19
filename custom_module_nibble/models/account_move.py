from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    nsfp = fields.Char(string="Nomor Seri Faktur Pajak (NSFP)")
    total_packaging = fields.Float(string="Total Packaging", compute="_compute_total_packaging", store=True)
    
    @api.depends('invoice_line_ids.packaging_qty')
    def _compute_total_packaging(self):
        for move in self:
            move.total_packaging = sum(move.invoice_line_ids.mapped('packaging_qty'))
            
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    packaging_qty = fields.Float(string="Packaging Quantity")
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override to set packaging_qty from sale_line_ids if available."""
        lines = super().create(vals_list)
        
        for line in lines:
            # If this invoice line is linked to sale order lines
            sale_lines = line.sale_line_ids
            if sale_lines:
                packaging_qty = 0
                for sale_line in sale_lines:
                    # Get stock moves related to this sale line that are done
                    moves = sale_line.move_ids.filtered(lambda m: m.state == 'done')
                    for move in moves:
                        if move.product_packaging_id:
                            packaging_qty += move.product_packaging_quantity
                        else:
                            # If no specific packaging is set but there's a quantity
                            if move.quantity > 0:
                                packaging_qty += move.quantity
                
                if packaging_qty > 0:
                    line.packaging_qty = packaging_qty
        
        return lines

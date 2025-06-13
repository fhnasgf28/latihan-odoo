from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    partner_ref = fields.Char(string="Vendor Reference")

    def button_validate(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for picking in self:
            if picking.picking_type_code != 'outgoing' or not picking.sale_id:
                continue
            sale_order = picking.sale_id
            if sale_order.delivery_tolerance > 0:
                tolerance_decimal = sale_order.delivery_tolerance
                for move in picking.move_ids_without_package:
                    so_line = move.sale_line_id
                    if not so_line:
                        continue
                    # Calculate quantities
                    ordered_qty = so_line.product_uom_qty
                    current_delivery_qty = sum(ml.quantity for ml in move.move_line_ids)
                    previously_delivered_qty = so_line.qty_delivered
                    total_potential_qty = previously_delivered_qty + current_delivery_qty
                    # Calculate maximum allowed quantity with tolerance
                    max_allowed_qty = ordered_qty * (1 + tolerance_decimal)
                    
                    # Check if delivery exceeds tolerance
                    if float_compare(total_potential_qty, max_allowed_qty, precision_digits=precision) > 0:
                        display_tolerance_percent = tolerance_decimal * 100
                        
                        raise UserError(_(
                            "Delivery Exceeds Tolerance Limit!\n\n"
                            f"Maximum Allowed: {max_allowed_qty:.2f} ({display_tolerance_percent:.2f}% tolerance)\n\n"
                            "Please adjust the delivery quantity to stay within tolerance limits."
                        ))

        return super(StockPicking, self).button_validate()

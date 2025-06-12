from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    partner_ref = fields.Char(string="Vendor Reference")

    def button_validate(self):
        print("button_validate farhan")
        for picking in self:
            sale = picking.sale_id
            if sale and sale.delivery_tolerance:
                tolerance = sale.delivery_tolerance / 100.0
                for move in picking.move_ids_without_package:
                    so_line = move.sale_line_id
                    if not so_line:
                        continue

                    ordered_qty = so_line.product_uom_qty
                    current_qty = sum(ml.quantity for ml in move.move_line_ids)
                    previous_qty = so_line.qty_delivered
                    total_delivered = previous_qty + current_qty
                    
                    max_allowed = ordered_qty * (1 + tolerance)
                    if total_delivered > max_allowed:
                        raise UserError(_(
                            f"Delivered quantity ({total_delivered}) exceeds allowed tolerance "
                            f"({sale.delivery_tolerance}%) for product '{so_line.product_id.display_name}'.\n\n"
                            f"Ordered: {ordered_qty}, Max Allowed: {max_allowed}"
                        ))

        return super(StockPicking, self).button_validate()

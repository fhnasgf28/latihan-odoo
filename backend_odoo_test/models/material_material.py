from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class Material(models.Model):
    _name = 'material.material'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Material Registration'

    material_code = fields.Char(string='Material Code', readonly=True,copy=False,help="Unique code for the material")
    material_name = fields.Char(string='Material Name', required=True,help="Name of the material")
    material_type = fields.Selection([
        ('fabric', 'Fabric'),
        ('jeans', 'Jeans'),
        ('cotton', 'Cotton'),
    ], string='Material Type', required=True,help="Type of the material (Fabric, Jeans, Cotton)")
    material_buy_price = fields.Float(string='Material Buy Price', required=True,help="Buying price of the material")
    supplier_id = fields.Many2one('res.partner', string='Related Supplier', required=True,domain=[('is_company', '=', True)],help="Supplier of this material")
    material_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', help="Unit of Measure for the material (e.g., Meter, KG, Unit)")
    min_stock_qty = fields.Float(string='Minimum Stock Quantity', default=0.0,help="Minimum quantity of material to keep in stock. Triggers alerts if below this.")
    current_stock_qty = fields.Float(string='Current Stock Quantity', compute='_compute_current_stock_qty', store=True,help="Current quantity of material available in stock.")
    material_lifecycle_stage = fields.Selection([
        ('new', 'New'),
        ('active', 'Active'),
        ('obsolete', 'Obsolete'),
        ('discontinued', 'Discontinued'),
    ], string='Lifecycle Stage', default='new',
        help="Current stage of the material in its lifecycle.")
    last_purchase_date = fields.Date(string='Last Purchase Date', compute='_compute_last_purchase_date', store=True, help="Date of the most recent purchase of this material.")
    product_id = fields.Many2one('product.product', string='Related Product', ondelete='restrict',help="Link to the standard Odoo product used for stock and purchase.",copy=False,domain="[('is_material_product', '=', True)]")  # Akan dibuat di product.product
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('archived', 'Archived'),
    ], string='Status', default='draft', readonly=True, copy=False, tracking=True,help="The current status of the material registration.")

    _sql_constraints = [
        ('material_code_unique', 'unique(material_code)', 'Material Code must be unique!'),
    ]

    @api.constrains('product_id')
    def _check_unique_product_id(self):
        for record in self:
            if record.product_id and self.search_count([('product_id', '=', record.product_id.id), ('id', '!=', record.id)]) > 0:
                raise ValidationError(_("Each Material must be linked to a unique Odoo Product. This product is already linked to another material."))

    @api.depends('product_id.qty_available')
    def _compute_current_stock_qty(self):
        for rec in self:
            rec.current_stock_qty = rec.product_id.qty_available if rec.product_id else 0.0

    @api.depends('product_id', 'product_id.purchase_order_line_ids.order_id.date_order',
                 'product_id.purchase_order_line_ids.state')
    def _compute_last_purchase_date(self):
        for rec in self:
            if rec.product_id:
                latest_po_line = self.env['purchase.order.line'].search([
                    ('product_id', '=', rec.product_id.id),
                    ('state', 'in', ['purchase', 'done'])
                ], limit=1)
                rec.last_purchase_date = latest_po_line.order_id.date_order if latest_po_line else False
            else:
                rec.last_purchase_date = False

    @api.constrains('material_buy_price')
    def _check_material_buy_price(self):
        for record in self:
            if record.material_buy_price < 100:
                raise ValidationError(_("Material Buy Price cannot be less than 100!"))

    @api.model
    def create(self, vals):
        if not vals.get('material_code'):
            vals['material_code'] = self.env['ir.sequence'].next_by_code('material.material.code') or _('New')
        if not vals.get('product_id'):
            product_name = vals.get('material_name')
            product_values = {
                'name': product_name,
                'default_code': vals.get('material_code'),
                'type': 'product',  # Storable product
                # 'uom_id': vals.get('material_uom_id'),
                'standard_price': vals.get('material_buy_price'),
                'is_material_product': True,
                'seller_ids': [(0, 0, {
                    'name': vals.get('supplier_id'),
                    'price': vals.get('material_buy_price')
                })]
            }
            product = self.env['product.product'].create(product_values)
            vals['product_id'] = product.id

        material = super(Material, self).create(vals)
        return material

    def write(self, vals):
        # Update related product.product when material fields change
        res = super(Material, self).write(vals)
        for record in self:
            if record.product_id:
                product_update_vals = {}
                if 'material_name' in vals:
                    product_update_vals['name'] = vals['material_name']
                if 'material_code' in vals:
                    product_update_vals['default_code'] = vals['material_code']
                # if 'material_uom_id' in vals:
                #     product_update_vals['uom_id'] = vals['material_uom_id']
                if 'material_buy_price' in vals:
                    product_update_vals['standard_price'] = vals['material_buy_price']
                if product_update_vals:
                    record.product_id.write(product_update_vals)
                # Update supplier info
                if 'supplier_id' in vals or 'material_buy_price' in vals:
                    supplier_id = vals.get('supplier_id', record.supplier_id.id)
                    buy_price = vals.get('material_buy_price', record.material_buy_price)
                    # Find or create seller info for the product
                    supplier_info = self.env['product.supplierinfo'].search([
                        ('product_id', '=', record.product_id.id),
                        ('name', '=', supplier_id)
                    ], limit=1)
                    if supplier_info:
                        supplier_info.write({'price': buy_price})
                    else:
                        self.env['product.supplierinfo'].create({
                            'product_id': record.product_id.id,
                            'name': supplier_id,
                            'price': buy_price,
                        })
        return res

    @api.depends('material_name')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = rec.material_name

    def unlink(self):
        products_to_unlink = self.env['product.product']
        for record in self:
            if record.product_id:
                # Add a check if the product is used in other sales/purchase orders
                if record.product_id.qty_available != 0 or \
                        self.env['sale.order.line'].search([('product_id', '=', record.product_id.id)], limit=1) or \
                        self.env['purchase.order.line'].search([('product_id', '=', record.product_id.id)], limit=1):
                    raise ValidationError(_("Cannot delete material '%s' because its associated product is still in stock or linked to existing sales/purchase orders. Please manage the product's lifecycle directly." % record.name))
                products_to_unlink |= record.product_id
        res = super(Material, self).unlink()
        if products_to_unlink:
            products_to_unlink.filtered(lambda p: p.is_material_product).unlink()

        return res

    def action_approve_material(self):
        """ Moves the material status to 'Approved'. """
        for rec in self:
            if rec.state == 'draft':
                rec.state = 'approved'
                rec.message_post(body=_("Material has been approved."))
            else:
                raise UserError(_("Material can only be approved from 'Draft' state."))

    def action_archive_material(self):
        """ Moves the material status to 'Archived'. """
        for rec in self:
            if rec.state in ['draft', 'approved']:
                rec.state = 'archived'
                if rec.product_id:
                    rec.product_id.active = False
                rec.message_post(body=_("Material has been archived."))
            else:
                raise UserError(_("Material can only be archived from 'Draft' or 'Approved' state."))

    def action_set_to_draft(self):
        """ Moves the material status back to 'Draft' from 'Archived'. """
        for rec in self:
            if rec.state == 'archived':
                rec.state = 'draft'
                if rec.product_id:
                    rec.product_id.active = True
                rec.message_post(body=_("Material has been set back to Draft."))
            else:
                raise UserError(_("Material can only be set to Draft from 'Archived' state."))
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Material(models.Model):
    _name = 'material.material'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Material Registration'

    material_code = fields.Char(string='Material Code', required=True, copy=False,
                                help="Unique code for the material")
    material_name = fields.Char(string='Material Name', required=True,
                                help="Name of the material")
    material_type = fields.Selection([
        ('fabric', 'Fabric'),
        ('jeans', 'Jeans'),
        ('cotton', 'Cotton'),
    ], string='Material Type', required=True,
       help="Type of the material (Fabric, Jeans, Cotton)")
    material_buy_price = fields.Float(string='Material Buy Price', required=True,
                                      help="Buying price of the material")
    # Using res.partner for supplier
    supplier_id = fields.Many2one('res.partner', string='Related Supplier', required=True,
                                  domain=[('is_company', '=', True)],
                                  help="Supplier of this material")

    _sql_constraints = [
        ('material_code_unique', 'unique(material_code)', 'Material Code must be unique!'),
    ]

    @api.constrains('material_buy_price')
    def _check_material_buy_price(self):
        for record in self:
            if record.material_buy_price < 100:
                raise ValidationError(_("Material Buy Price cannot be less than 100!"))

    @api.model
    def create(self, vals):
        if 'material_code' not in vals or not vals['material_code']:
            vals['material_code'] = self.env['ir.sequence'].next_by_code('material.material.code') or _('New')
        return super(Material, self).create(vals)
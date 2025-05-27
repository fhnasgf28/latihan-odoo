from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _description = 'Material Product Template'

    is_material = fields.Boolean(string='Is a Material', default=False,
                                 help="Tick if this product represents a raw material.")

    @api.constrains('is_material')
    def _check_material_type_attribute_for_material(self):
        # Contoh validasi: Jika is_material true, pastikan ada atribut Material Type
        material_type_attribute = self.env.ref('material_registration.product_attribute_material_type', raise_if_not_found=False)
        if material_type_attribute:
            for record in self:
                if record.is_material and not any(attr_line.attribute_id == material_type_attribute for attr_line in record.attribute_line_ids):
                    # Odoo akan membuat varian otomatis, jadi pastikan atribut ini ada
                    # Anda bisa menambahkan logika untuk menambahkan attribute_line_ids secara otomatis
                    pass # Contoh sederhana, validasi kompleks mungkin di product.product

class ProductProduct(models.Model):
    _inherit = 'product.product'
    _description = 'Material Product Variant'

    supplier_ids = fields.One2many( 'product.supplierinfo', 'product_tmpl_id',string='Vendors', related='product_tmpl_id.seller_ids'
    )

    @api.constrains('standard_price')
    def _check_material_buy_price_min(self):
        for record in self:
            if record.product_tmpl_id.is_material and record.standard_price < 100:
                raise ValidationError(_("Material Buy Price (Cost) cannot be less than 100!"))


from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _description = 'Material Product Template'

    is_material = fields.Boolean(string='Is a Material', default=False, help="Tick if this product represents a raw material.")

    @api.constrains('is_material', 'attribute_line_ids')
    def _check_material_type_attribute_for_material(self):
        """
        Ensures that if a product template is marked as a material,
        it has the 'Material Type' attribute associated with it.
        """
        # Get the 'Material Type' attribute record
        material_type_attribute = self.env.ref('backend_odoo_test.product_attribute_material_type', raise_if_not_found=False)
        if not material_type_attribute:
            raise ValidationError(_("Configuration Error: 'Material Type' attribute (product_attribute_material_type) not found. Please ensure your module data is loaded correctly."))
        for record in self:
            if record.is_material:
                # Check if 'Material Type' attribute is present in the attribute lines of the product template
                has_material_type_attribute = any(
                    attr_line.attribute_id == material_type_attribute
                    for attr_line in record.attribute_line_ids
                )
                if not has_material_type_attribute:
                    raise ValidationError(
                        _("Material '%s' must have a 'Material Type' attribute selected. "
                          "Please add the 'Material Type' attribute in the 'Attributes & Variants' tab."
                          % record.name)
                    )

class ProductProduct(models.Model):
    _inherit = 'product.product'
    _description = 'Material Product Variant'

    supplier_ids = fields.One2many( 'product.supplierinfo', 'product_tmpl_id',string='Vendors', related='product_tmpl_id.seller_ids')
    is_material_product = fields.Boolean(string='Is a Material Product', default=False,help="Internal flag to identify products linked to the custom Material model.")
    material_id = fields.One2many('material.material', 'product_id', string='Linked Material',help="The custom Material record linked to this Odoo product.",readonly=True)

    @api.constrains('standard_price')
    def _check_material_buy_price_min(self):
        for record in self:
            if record.product_tmpl_id.is_material and record.standard_price < 100:
                raise ValidationError(_("Material Buy Price (Cost) cannot be less than 100!"))


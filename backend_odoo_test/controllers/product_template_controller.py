from odoo import http
from odoo.http import request, Response
import json


class MaterialController(http.Controller):
    _inherit = 'web.controller'

    # Helper function to get product info for API response
    def _prepare_material_data(self, material_product):
        # material_product is product.product record
        product_template = material_product.product_tmpl_id
        material_type_attribute = request.env.ref('material_registration.product_attribute_material_type',
                                                  raise_if_not_found=False)
        material_type = None
        if material_type_attribute:
            for attribute_value in material_product.product_template_attribute_value_ids:
                if attribute_value.attribute_id == material_type_attribute:
                    material_type = attribute_value.name
                    break

        supplier_info = material_product.seller_ids and material_product.seller_ids[0] or False
        # Get current stock quantity
        stock_quantity = material_product.qty_available  # Odoo's standard quantity on hand

        return {
            'id': material_product.id,
            'product_template_id': product_template.id,
            'default_code': material_product.default_code,  # SKU/Material Code
            'material_name': material_product.display_name,  # Includes variant name
            'material_type': material_type,  # Attribute value
            'material_buy_price': material_product.standard_price,  # Cost
            'supplier_name': supplier_info.partner_id.name if supplier_info else None,
            'supplier_id': supplier_info.partner_id.id if supplier_info else None,
            'current_stock_quantity': stock_quantity,
        }

    @http.route('/api/materials', type='http', auth='user', methods=['GET'], csrf=False)
    def get_all_materials(self, material_type=None, **kw):
        """
        API endpoint to retrieve all materials or filter by material type.
        Usage: GET /api/materials?material_type=fabric
        """
        domain = [('product_tmpl_id.is_material', '=', True)]  # Filter for materials only

        if material_type:
            material_type_attribute = request.env.ref('material_registration.product_attribute_material_type',
                                                      raise_if_not_found=False)
            if not material_type_attribute:
                return Response(json.dumps({'error': 'Material Type attribute not configured.'}),
                                status=500, mimetype='application/json')

            # Find the attribute value ID for the given material_type
            material_type_value = request.env['product.attribute.value'].sudo().search([
                ('attribute_id', '=', material_type_attribute.id),
                ('name', 'ilike', material_type)
            ], limit=1)

            if not material_type_value:
                return Response(json.dumps({'error': f'Invalid material_type: {material_type}.'}),
                                status=400, mimetype='application/json')

            # Filter products by their attribute values
            domain.append(
                ('product_template_attribute_value_ids.product_attribute_value_id', '=', material_type_value.id))

        materials = request.env['product.product'].sudo().search(domain)
        material_data = [self._prepare_material_data(m) for m in materials]

        return Response(json.dumps(material_data), status=200, mimetype='application/json')

    @http.route('/api/materials/<int:material_id>', type='http', auth='user', methods=['GET'], csrf=False)
    def get_material_by_id(self, material_id, **kw):
        """
        API endpoint to retrieve a single material by ID.
        Usage: GET /api/materials/1 (where ID is product.product ID)
        """
        material = request.env['product.product'].sudo().browse(material_id)
        if not material.exists() or not material.product_tmpl_id.is_material:
            return Response(json.dumps({'error': 'Material not found or not a material type.'}), status=404,
                            mimetype='application/json')

        material_data = self._prepare_material_data(material)
        return Response(json.dumps(material_data), status=200, mimetype='application/json')

    @http.route('/api/materials', type='json', auth='user', methods=['POST'], csrf=False)
    def create_material(self, **post):
        """
        API endpoint to create a new material (product.template and product.product).
        This will create a new product.template and product.product if not using variants,
        or add a variant if using variants.

        Body (JSON):
        {
            "material_name": "New Fabric Roll",
            "material_type": "fabric", // This will map to an attribute value
            "material_buy_price": 120.50,
            "supplier_id": 1,
            "default_code": "NEW_FAB_001" // Optional, maps to SKU
        }
        """
        try:
            data = request.jsonrequest

            required_fields = ['material_name', 'material_type', 'material_buy_price', 'supplier_id']
            for field in required_fields:
                if field not in data:
                    return {'error': f'Missing required field: {field}'}, 400

            if data.get('material_buy_price') < 100:
                return {'error': 'Material Buy Price (Cost) cannot be less than 100!'}, 400

            supplier = request.env['res.partner'].sudo().browse(data['supplier_id'])
            if not supplier.exists() or not supplier.is_company:
                return {'error': 'Invalid or non-company supplier_id.'}, 400

            material_type_attribute = request.env.ref('material_registration.product_attribute_material_type',
                                                      raise_if_not_found=False)
            if not material_type_attribute:
                return {'error': 'Material Type attribute not configured.'}, 500

            material_type_value = request.env['product.attribute.value'].sudo().search([
                ('attribute_id', '=', material_type_attribute.id),
                ('name', 'ilike', data['material_type'])
            ], limit=1)

            if not material_type_value:
                return {
                    'error': f'Invalid material_type value: {data["material_type"]}. Please create it first in Odoo as a Material Type attribute value.'}, 400

            # Create/find product template
            product_template_vals = {
                'name': data['material_name'],
                'is_material': True,
                'type': 'product',  # Standard Odoo product type for storable items
                'default_code': data.get('default_code'),  # Set SKU if provided
                'attribute_line_ids': [
                    (0, 0, {
                        'attribute_id': material_type_attribute.id,
                        'value_ids': [(6, 0, [material_type_value.id])]
                    })
                ]
            }
            # Search for existing template with the same name and is_material=True
            product_template = request.env['product.template'].sudo().search([
                ('name', '=', data['material_name']),
                ('is_material', '=', True)
            ], limit=1)

            if not product_template:
                product_template = request.env['product.template'].sudo().create(product_template_vals)
            else:
                # If template exists, ensure the material_type attribute line is added
                if not any(attr_line.attribute_id == material_type_attribute for attr_line in
                           product_template.attribute_line_ids):
                    product_template.write({
                        'attribute_line_ids': [
                            (0, 0, {
                                'attribute_id': material_type_attribute.id,
                                'value_ids': [(6, 0, [material_type_value.id])]
                            })
                        ]
                    })

            # Odoo automatically creates product.product variants based on attribute lines.
            # We need to find the specific variant, or assume the first one if no other attributes.
            product_variant = product_template.product_variant_ids.filtered(
                lambda p: material_type_value in p.product_template_attribute_value_ids.product_attribute_value_id
            )

            if not product_variant:  # Fallback if specific variant not found or no attributes
                product_variant = product_template.product_variant_ids and product_template.product_variant_ids[0]

            if not product_variant:
                return {'error': 'Failed to create or find product variant.'}, 500

            # Update standard_price (cost) and supplier info on the product.product
            product_variant.sudo().write({
                'standard_price': data['material_buy_price']
            })

            # Create or update supplier info
            supplierinfo = request.env['product.supplierinfo'].sudo().search([
                ('product_tmpl_id', '=', product_template.id),
                ('name', '=', supplier.id),
                ('product_id', '=', product_variant.id)  # Link to specific variant
            ], limit=1)

            if not supplierinfo:
                request.env['product.supplierinfo'].sudo().create({
                    'product_tmpl_id': product_template.id,
                    'product_id': product_variant.id,
                    'name': supplier.id,
                    'price': data['material_buy_price'],
                })
            else:
                supplierinfo.sudo().write({'price': data['material_buy_price']})

            return {'id': product_variant.id, 'default_code': product_variant.default_code,
                    'message': 'Material created/updated successfully'}, 201
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500

    @http.route('/api/materials/<int:material_id>', type='json', auth='user', methods=['PUT'], csrf=False)
    def update_material(self, material_id, **post):
        """
        API endpoint to update an existing material (product.product).
        Usage: PUT /api/materials/1 (where ID is product.product ID)
        Body (JSON):
        {
            "material_name": "Updated Fabric Roll",
            "material_buy_price": 250.00,
            "material_type": "jeans", // To change variant type
            "supplier_id": 2
        }
        """
        try:
            material_product = request.env['product.product'].sudo().browse(material_id)
            if not material_product.exists() or not material_product.product_tmpl_id.is_material:
                return {'error': 'Material not found or not a material type.'}, 404

            data = request.jsonrequest

            # Update standard_price (cost)
            if 'material_buy_price' in data:
                if data['material_buy_price'] < 100:
                    return {'error': 'Material Buy Price (Cost) cannot be less than 100!'}, 400
                material_product.sudo().write({'standard_price': data['material_buy_price']})

            # Update supplier if provided
            if 'supplier_id' in data:
                supplier = request.env['res.partner'].sudo().browse(data['supplier_id'])
                if not supplier.exists() or not supplier.is_company:
                    return {'error': 'Invalid or non-company supplier_id.'}, 400

                # Update/create supplierinfo
                supplierinfo = request.env['product.supplierinfo'].sudo().search([
                    ('product_tmpl_id', '=', material_product.product_tmpl_id.id),
                    ('name', '=', supplier.id),
                    ('product_id', '=', material_product.id)
                ], limit=1)

                if not supplierinfo:
                    request.env['product.supplierinfo'].sudo().create({
                        'product_tmpl_id': material_product.product_tmpl_id.id,
                        'product_id': material_product.id,
                        'name': supplier.id,
                        'price': data.get('material_buy_price', material_product.standard_price),
                    })
                else:
                    supplierinfo.sudo().write(
                        {'price': data.get('material_buy_price', material_product.standard_price)})

            # Update material_name (product_template name)
            if 'material_name' in data:
                material_product.product_tmpl_id.sudo().write({'name': data['material_name']})

            # Update material_type (changing variant attributes)
            if 'material_type' in data:
                material_type_attribute = request.env.ref('material_registration.product_attribute_material_type',
                                                          raise_if_not_found=False)
                if not material_type_attribute:
                    return {'error': 'Material Type attribute not configured.'}, 500

                new_material_type_value = request.env['product.attribute.value'].sudo().search([
                    ('attribute_id', '=', material_type_attribute.id),
                    ('name', 'ilike', data['material_type'])
                ], limit=1)

                if not new_material_type_value:
                    return {'error': f'Invalid material_type value: {data["material_type"]}.'}, 400

                # Check if the desired variant already exists
                existing_variant = material_product.product_tmpl_id.product_variant_ids.filtered(
                    lambda
                        p: new_material_type_value in p.product_template_attribute_value_ids.product_attribute_value_id
                )
                if existing_variant and existing_variant != material_product:
                    return {
                        'error': f'A variant with material type {data["material_type"]} already exists. Please update that variant directly.'}, 400

            return {'id': material_product.id, 'message': 'Material updated successfully'}, 200
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500

    @http.route('/api/materials/<int:material_id>', type='http', auth='user', methods=['DELETE'], csrf=False)
    def delete_material(self, material_id, **kw):
        """
        API endpoint to delete a material by ID (product.product).
        Usage: DELETE /api/materials/1
        """
        try:
            material_product = request.env['product.product'].sudo().browse(material_id)
            if not material_product.exists() or not material_product.product_tmpl_id.is_material:
                return Response(json.dumps({'error': 'Material not found or not a material type.'}), status=404,
                                mimetype='application/json')

            # Odoo's product.product.unlink() handles related stock moves and supplier info.
            material_product.sudo().unlink()
            return Response(json.dumps({'message': 'Material deleted successfully'}), status=200,
                            mimetype='application/json')
        except Exception as e:
            return Response(json.dumps({'error': str(e)}), status=500, mimetype='application/json')

    # Example for getting stock quantity for a material
    @http.route('/api/materials/<int:material_id>/stock', type='http', auth='user', methods=['GET'], csrf=False)
    def get_material_stock(self, material_id, **kw):
        """
        API endpoint to get current stock quantity for a specific material.
        Usage: GET /api/materials/1/stock
        """
        material_product = request.env['product.product'].sudo().browse(material_id)
        if not material_product.exists() or not material_product.product_tmpl_id.is_material:
            return Response(json.dumps({'error': 'Material not found or not a material type.'}), status=404,
                            mimetype='application/json')

        stock_data = {
            'material_id': material_product.id,
            'material_name': material_product.display_name,
            'current_quantity_on_hand': material_product.qty_available,
            'forecasted_quantity': material_product.virtual_available,
        }
        return Response(json.dumps(stock_data), status=200, mimetype='application/json')

    # Example for getting purchase history for a material
    @http.route('/api/materials/<int:material_id>/purchase_history', type='http', auth='user', methods=['GET'],
                csrf=False)
    def get_material_purchase_history(self, material_id, **kw):
        """
        API endpoint to get purchase order history for a specific material.
        Usage: GET /api/materials/1/purchase_history
        """
        material_product = request.env['product.product'].sudo().browse(material_id)
        if not material_product.exists() or not material_product.product_tmpl_id.is_material:
            return Response(json.dumps({'error': 'Material not found or not a material type.'}), status=404,
                            mimetype='application/json')

        purchase_lines = request.env['purchase.order.line'].sudo().search([
            ('product_id', '=', material_product.id),
            ('state', 'in', ['purchase', 'done'])
        ], order='date_order desc')

        history_data = []
        for line in purchase_lines:
            history_data.append({
                'purchase_order_id': line.order_id.id,
                'purchase_order_name': line.order_id.name,
                'supplier_name': line.partner_id.name,
                'quantity': line.product_qty,
                'price_unit': line.price_unit,
                'order_date': str(line.order_id.date_order),
                'state': line.state,
            })

        return Response(json.dumps(history_data), status=200, mimetype='application/json')
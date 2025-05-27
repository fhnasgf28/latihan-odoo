from odoo import http
from odoo.http import request, Response
import json


class MaterialController(http.Controller):
    _inherit = 'web.controller'

    @http.route('/api/materials', type='http', auth='user', methods=['GET'], csrf=False)
    def get_all_materials(self, material_type=None, **kw):
        """
        API endpoint to retrieve all materials or filter by material type.
        Usage: GET /api/materials?material_type=fabric
        """
        domain = []
        if material_type:
            # Validate material_type to prevent invalid input
            allowed_types = ['fabric', 'jeans', 'cotton']
            if material_type.lower() not in allowed_types:
                return Response(
                    json.dumps({'error': 'Invalid material_type. Allowed types are: fabric, jeans, cotton.'}),
                    status=400, mimetype='application/json')
            domain.append(('material_type', '=', material_type.lower()))

        materials = request.env['material.material'].sudo().search(domain)
        material_data = []
        for material in materials:
            material_data.append({
                'id': material.id,
                'material_code': material.material_code,
                'material_name': material.material_name,
                'material_type': material.material_type,
                'material_buy_price': material.material_buy_price,
                'supplier_name': material.supplier_id.name,
                'supplier_id': material.supplier_id.id,
            })
        return Response(json.dumps(material_data), status=200, mimetype='application/json')

    @http.route('/api/materials/<int:material_id>', type='http', auth='user', methods=['GET'], csrf=False)
    def get_material_by_id(self, material_id, **kw):
        """
        API endpoint to retrieve a single material by ID.
        Usage: GET /api/materials/1
        """
        material = request.env['material.material'].sudo().browse(material_id)
        if not material.exists():
            return Response(json.dumps({'error': 'Material not found.'}), status=404, mimetype='application/json')

        material_data = {
            'id': material.id,
            'material_code': material.material_code,
            'material_name': material.material_name,
            'material_type': material.material_type,
            'material_buy_price': material.material_buy_price,
            'supplier_name': material.supplier_id.name,
            'supplier_id': material.supplier_id.id,
        }
        return Response(json.dumps(material_data), status=200, mimetype='application/json')

    @http.route('/api/materials', type='json', auth='user', methods=['POST'], csrf=False)
    def create_material(self, **post):
        """
        API endpoint to create a new material.
        Usage: POST /api/materials
        Body (JSON):
        {
            "material_name": "New Fabric",
            "material_type": "fabric",
            "material_buy_price": 120.50,
            "supplier_id": 1
        }
        (material_code will be auto-generated if not provided)
        """
        try:
            data = request.jsonrequest

            # Basic validation
            required_fields = ['material_name', 'material_type', 'material_buy_price', 'supplier_id']
            for field in required_fields:
                if field not in data:
                    return {'error': f'Missing required field: {field}'}, 400

            # Check material_buy_price constraint
            if data.get('material_buy_price') < 100:
                return {'error': 'Material Buy Price cannot be less than 100!'}, 400

            # Check if supplier_id exists
            supplier = request.env['res.partner'].sudo().browse(data['supplier_id'])
            if not supplier.exists() or not supplier.is_company:
                return {'error': 'Invalid or non-company supplier_id.'}, 400

            # Validate material_type
            allowed_types = ['fabric', 'jeans', 'cotton']
            if data['material_type'].lower() not in allowed_types:
                return {'error': 'Invalid material_type. Allowed types are: fabric, jeans, cotton.'}, 400

            vals = {
                'material_code': data.get('material_code'),  # Optional, will be auto-generated if not provided
                'material_name': data['material_name'],
                'material_type': data['material_type'].lower(),
                'material_buy_price': data['material_buy_price'],
                'supplier_id': data['supplier_id'],
            }

            material = request.env['material.material'].sudo().create(vals)
            return {'id': material.id, 'material_code': material.material_code,
                    'message': 'Material created successfully'}, 201
        except Exception as e:
            return {'error': str(e)}, 500

    @http.route('/api/materials/<int:material_id>', type='json', auth='user', methods=['PUT'], csrf=False)
    def update_material(self, material_id, **post):
        """
        API endpoint to update an existing material.
        Usage: PUT /api/materials/1
        Body (JSON):
        {
            "material_name": "Updated Fabric",
            "material_buy_price": 150.00
        }
        """
        try:
            material = request.env['material.material'].sudo().browse(material_id)
            if not material.exists():
                return {'error': 'Material not found.'}, 404

            data = request.jsonrequest

            # Validate material_buy_price constraint if updated
            if 'material_buy_price' in data and data['material_buy_price'] < 100:
                return {'error': 'Material Buy Price cannot be less than 100!'}, 400

            # Validate material_type if updated
            if 'material_type' in data:
                allowed_types = ['fabric', 'jeans', 'cotton']
                if data['material_type'].lower() not in allowed_types:
                    return {'error': 'Invalid material_type. Allowed types are: fabric, jeans, cotton.'}, 400
                data['material_type'] = data['material_type'].lower()  # Ensure lowercase for consistency

            # Check if supplier_id exists if updated
            if 'supplier_id' in data:
                supplier = request.env['res.partner'].sudo().browse(data['supplier_id'])
                if not supplier.exists() or not supplier.is_company:
                    return {'error': 'Invalid or non-company supplier_id.'}, 400

            material.write(data)
            return {'id': material.id, 'message': 'Material updated successfully'}, 200
        except Exception as e:
            return {'error': str(e)}, 500

    @http.route('/api/materials/<int:material_id>', type='http', auth='user', methods=['DELETE'], csrf=False)
    def delete_material(self, material_id, **kw):
        """
        API endpoint to delete a material by ID.
        Usage: DELETE /api/materials/1
        """
        try:
            material = request.env['material.material'].sudo().browse(material_id)
            if not material.exists():
                return Response(json.dumps({'error': 'Material not found.'}), status=404, mimetype='application/json')

            material.unlink()
            return Response(json.dumps({'message': 'Material deleted successfully'}), status=200,
                            mimetype='application/json')
        except Exception as e:
            return Response(json.dumps({'error': str(e)}), status=500, mimetype='application/json')
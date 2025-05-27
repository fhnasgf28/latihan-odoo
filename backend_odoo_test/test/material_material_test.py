from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestMaterial(TransactionCase):

    def setUp(self):
        super(TestMaterial, self).setUp()
        self.Material = self.env['material.material']
        self.Supplier = self.env['res.partner']

        # Create a test supplier
        self.test_supplier = self.Supplier.create({
            'name': 'Test Supplier Co.',
            'is_company': True,
        })

    def test_create_material_valid(self):
        """Test creating a material with valid data."""
        material = self.Material.create({
            'material_name': 'Cotton Basic',
            'material_type': 'cotton',
            'material_buy_price': 150.00,
            'supplier_id': self.test_supplier.id,
        })
        self.assertTrue(material.exists())
        self.assertEqual(material.material_name, 'Cotton Basic')
        self.assertEqual(material.material_type, 'cotton')
        self.assertEqual(material.material_buy_price, 150.00)
        self.assertEqual(material.supplier_id, self.test_supplier)
        self.assertTrue(material.material_code.startswith('MAT/'))

    def test_create_material_buy_price_less_than_100(self):
        """Test creating a material with buy price less than 100 should raise ValidationError."""
        with self.assertRaises(ValidationError):
            self.Material.create({
                'material_name': 'Invalid Fabric',
                'material_type': 'fabric',
                'material_buy_price': 99.99,
                'supplier_id': self.test_supplier.id,
            })

    def test_create_material_missing_required_fields(self):
        """Test creating a material with missing required fields."""
        with self.assertRaises(Exception): # Odoo will raise a psycopg2.IntegrityError or similar for missing required fields
            self.Material.create({
                'material_name': 'Incomplete Material',
                'material_type': 'fabric',
                # material_buy_price and supplier_id are missing
            })

    def test_update_material_valid(self):
        """Test updating an existing material."""
        material = self.Material.create({
            'material_name': 'Old Fabric',
            'material_type': 'fabric',
            'material_buy_price': 200.00,
            'supplier_id': self.test_supplier.id,
        })
        material.write({
            'material_name': 'Updated Fabric',
            'material_buy_price': 250.00,
            'material_type': 'jeans',
        })
        self.assertEqual(material.material_name, 'Updated Fabric')
        self.assertEqual(material.material_buy_price, 250.00)
        self.assertEqual(material.material_type, 'jeans')

    def test_update_material_buy_price_less_than_100(self):
        """Test updating material buy price to less than 100 should raise ValidationError."""
        material = self.Material.create({
            'material_name': 'Good Material',
            'material_type': 'cotton',
            'material_buy_price': 150.00,
            'supplier_id': self.test_supplier.id,
        })
        with self.assertRaises(ValidationError):
            material.write({'material_buy_price': 50.00})

    def test_delete_material(self):
        """Test deleting a material."""
        material = self.Material.create({
            'material_name': 'Material to Delete',
            'material_type': 'jeans',
            'material_buy_price': 120.00,
            'supplier_id': self.test_supplier.id,
        })
        material_id = material.id
        material.unlink()
        self.assertFalse(self.Material.browse(material_id).exists())

    def test_material_code_unique(self):
        """Test material code uniqueness constraint."""
        material1 = self.Material.create({
            'material_code': 'TESTCODE1',
            'material_name': 'Material A',
            'material_type': 'fabric',
            'material_buy_price': 100.00,
            'supplier_id': self.test_supplier.id,
        })
        with self.assertRaisesRegex(Exception, "Material Code must be unique!"): # Odoo will raise a UserError wrapped around a psycopg2.IntegrityError
            self.Material.create({
                'material_code': 'TESTCODE1',
                'material_name': 'Material B',
                'material_type': 'cotton',
                'material_buy_price': 110.00,
                'supplier_id': self.test_supplier.id,
            })
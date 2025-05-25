from odoo import models, fields, api


class odoo_owl_framework(models.Model):
    _name = 'owl.note'
    _description = 'odoo_owl_framework.odoo_owl_framework'

    name = fields.Char(string='Name', required=True)
    content = fields.Text(string='Content')




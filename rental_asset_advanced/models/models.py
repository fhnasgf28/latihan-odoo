# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class rental_asset_advanced(models.Model):
#     _name = 'rental_asset_advanced.rental_asset_advanced'
#     _description = 'rental_asset_advanced.rental_asset_advanced'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

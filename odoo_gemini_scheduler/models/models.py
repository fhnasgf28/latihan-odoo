# from odoo import models, fields, api


# class odoo_gemini_scheduler(models.Model):
#     _name = 'odoo_gemini_scheduler.odoo_gemini_scheduler'
#     _description = 'odoo_gemini_scheduler.odoo_gemini_scheduler'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100


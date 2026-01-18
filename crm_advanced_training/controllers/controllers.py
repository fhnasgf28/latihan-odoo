# from odoo import http


# class CrmAdvancedTraining(http.Controller):
#     @http.route('/crm_advanced_training/crm_advanced_training', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/crm_advanced_training/crm_advanced_training/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('crm_advanced_training.listing', {
#             'root': '/crm_advanced_training/crm_advanced_training',
#             'objects': http.request.env['crm_advanced_training.crm_advanced_training'].search([]),
#         })

#     @http.route('/crm_advanced_training/crm_advanced_training/objects/<model("crm_advanced_training.crm_advanced_training"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('crm_advanced_training.object', {
#             'object': obj
#         })


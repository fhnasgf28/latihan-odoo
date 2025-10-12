# from odoo import http


# class OdooGeminiScheduler(http.Controller):
#     @http.route('/odoo_gemini_scheduler/odoo_gemini_scheduler', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/odoo_gemini_scheduler/odoo_gemini_scheduler/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('odoo_gemini_scheduler.listing', {
#             'root': '/odoo_gemini_scheduler/odoo_gemini_scheduler',
#             'objects': http.request.env['odoo_gemini_scheduler.odoo_gemini_scheduler'].search([]),
#         })

#     @http.route('/odoo_gemini_scheduler/odoo_gemini_scheduler/objects/<model("odoo_gemini_scheduler.odoo_gemini_scheduler"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('odoo_gemini_scheduler.object', {
#             'object': obj
#         })


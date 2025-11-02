# from odoo import http


# class ProjectCustomInherit(http.Controller):
#     @http.route('/project_custom_inherit/project_custom_inherit', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/project_custom_inherit/project_custom_inherit/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('project_custom_inherit.listing', {
#             'root': '/project_custom_inherit/project_custom_inherit',
#             'objects': http.request.env['project_custom_inherit.project_custom_inherit'].search([]),
#         })

#     @http.route('/project_custom_inherit/project_custom_inherit/objects/<model("project_custom_inherit.project_custom_inherit"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('project_custom_inherit.object', {
#             'object': obj
#         })


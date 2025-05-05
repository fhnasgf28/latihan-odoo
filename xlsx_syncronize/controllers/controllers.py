# from odoo import http


# class XlsxSyncronize(http.Controller):
#     @http.route('/xlsx_syncronize/xlsx_syncronize', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/xlsx_syncronize/xlsx_syncronize/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('xlsx_syncronize.listing', {
#             'root': '/xlsx_syncronize/xlsx_syncronize',
#             'objects': http.request.env['xlsx_syncronize.xlsx_syncronize'].search([]),
#         })

#     @http.route('/xlsx_syncronize/xlsx_syncronize/objects/<model("xlsx_syncronize.xlsx_syncronize"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('xlsx_syncronize.object', {
#             'object': obj
#         })


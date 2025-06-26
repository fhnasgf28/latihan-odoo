# -*- coding: utf-8 -*-
# from odoo import http


# class DocumentExpiryModul(http.Controller):
#     @http.route('/document_expiry_modul/document_expiry_modul', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/document_expiry_modul/document_expiry_modul/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('document_expiry_modul.listing', {
#             'root': '/document_expiry_modul/document_expiry_modul',
#             'objects': http.request.env['document_expiry_modul.document_expiry_modul'].search([]),
#         })

#     @http.route('/document_expiry_modul/document_expiry_modul/objects/<model("document_expiry_modul.document_expiry_modul"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('document_expiry_modul.object', {
#             'object': obj
#         })


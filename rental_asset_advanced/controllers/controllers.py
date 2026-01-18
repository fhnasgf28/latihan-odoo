# -*- coding: utf-8 -*-
# from odoo import http


# class RentalAssetAdvanced(http.Controller):
#     @http.route('/rental_asset_advanced/rental_asset_advanced/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rental_asset_advanced/rental_asset_advanced/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('rental_asset_advanced.listing', {
#             'root': '/rental_asset_advanced/rental_asset_advanced',
#             'objects': http.request.env['rental_asset_advanced.rental_asset_advanced'].search([]),
#         })

#     @http.route('/rental_asset_advanced/rental_asset_advanced/objects/<model("rental_asset_advanced.rental_asset_advanced"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rental_asset_advanced.object', {
#             'object': obj
#         })

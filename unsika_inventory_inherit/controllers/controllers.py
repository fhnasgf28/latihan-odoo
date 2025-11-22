# from odoo import http


# class UnsikaInventoryInherit(http.Controller):
#     @http.route('/unsika_inventory_inherit/unsika_inventory_inherit', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/unsika_inventory_inherit/unsika_inventory_inherit/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('unsika_inventory_inherit.listing', {
#             'root': '/unsika_inventory_inherit/unsika_inventory_inherit',
#             'objects': http.request.env['unsika_inventory_inherit.unsika_inventory_inherit'].search([]),
#         })

#     @http.route('/unsika_inventory_inherit/unsika_inventory_inherit/objects/<model("unsika_inventory_inherit.unsika_inventory_inherit"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('unsika_inventory_inherit.object', {
#             'object': obj
#         })


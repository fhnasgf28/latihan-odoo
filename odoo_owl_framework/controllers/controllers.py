from odoo import http
from odoo.http import request

class OdooOwlFramework(http.Controller):
    @http.route('/odoo_owl_demo', auth='public',type='http', website=True)
    def index(self, **kw):
        return request.render('odoo_owl_framework.odoo_owl_template')



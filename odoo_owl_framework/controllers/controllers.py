from odoo import http
from odoo.http import request
import json

class OdooOwlFramework(http.Controller):
    @http.route('/odoo_owl_demo', auth='public',type='http', website=True)
    def index(self, **kw):
        return request.render('odoo_owl_framework.odoo_owl_template')

    @http.route('/odoo_owl_todo', auth='public',type='http', website=True)
    def todo_page(self):
        return request.render('odoo_owl_framework.todo_page_template')

    @http.route('/odoo_owl_todo/get_tasks', auth='public',type='http', website=True)
    def get_tasks(self):
        return {
            'tasks': [
                {"id": 1, "text": "Belajar OWL"},
                {"id": 2, "text": "Coba RPC call"},
            ]
        }

    @http.route('/odoo_owl_todo/add_task', auth='public',type='json')
    def add_task(self, text):
        return {"status": "ok", "text": text}



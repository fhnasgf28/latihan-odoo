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

    @http.route('/odoo_owl_todo/owl_crud', auth='user',type='http', website=True)
    def owl_crud_page(self):
        return request.render('odoo_owl_framework.owl_crud_template')

    @http.route('/odoo_owl_todo/api/notes', type='json', auth='user')
    def get_notes(self):
        notes = request.env['owl.note'].sudo().search([])
        return [
            {
                'id': note.id,
                'title': note.title,
                'content': note.content,
            }
            for note in notes
        ]

    @http.route('/odoo_owl_todo/api/notes/create', type='json', auth='public')
    def create_note(self, **kwargs):
        note = request.env['owl.note'].sudo().create({
            'title': kwargs.get('name'),
            'content': kwargs.get('content'),
        })
        return {
            'id': note.id,
            'title': note.title,
            'content': note.content,
        }




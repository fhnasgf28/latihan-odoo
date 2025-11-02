from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    project_type = fields.Selection(
        selection=[
            ('internal', 'Internal'),
            ('external', 'Eksternal/Klien'),
            ('rd', 'R&D'),],string="Tipe Proyek",default='internal',required=True)
    total_budget = fields.Monetary(string="Total Budget",currency_field='currency_id',help="Total anggaran yang disetujui untuk proyek ini.")

    scope_of_work = fields.Html(string="Scope of Work (SOW)",help="Penjelasan detail mengenai apa saja yang akan dikerjakan dalam proyek ini.")
    client_contact_id = fields.Many2one('res.partner',string="Kontak Klien (PIC)",help="Narahubung utama di sisi klien.")


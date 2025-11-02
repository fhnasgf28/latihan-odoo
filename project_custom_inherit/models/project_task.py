# -*- coding: utf-8 -*-

from odoo import models, fields


class ProjectTask(models.Model):
    _inherit = 'project.task'  # <-- Meng-inherit model project.task

    task_priority = fields.Selection(
        selection=[
            ('0', 'Rendah'),
            ('1', 'Sedang'),
            ('2', 'Tinggi'),
            ('3', 'Kritis'),
        ],
        string="Prioritas",
        default='1',
    )

    is_billable = fields.Boolean(
        string="Bisa Ditagih (Billable)",
        default=True,
        help="Tandai jika waktu yang dihabiskan untuk tugas ini dapat ditagihkan ke klien."
    )

    task_type = fields.Selection(
        selection=[
            ('feature', 'New Feature'),
            ('bug', 'Bug Fixing'),
            ('research', 'Research'),
            ('meeting', 'Meeting'),
            ('other', 'Lainnya'),
        ],
        string="Tipe Tugas",
        default='feature',
    )
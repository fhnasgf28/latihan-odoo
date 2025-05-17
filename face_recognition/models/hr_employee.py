from odoo import models, fields, api
import json


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    face_image = fields.Binary(string='Face Image')
    face_encoding = fields.Char(string='Face Encoding')

    _sql_constraints = [
        ('unique_face_encoding_employee', 'unique(id, face_encoding)',
         'Setiap karyawan harus memiliki encoding wajah yang unik!'),
    ]


    def set_face_encoding(self, encoding_list, image_data=False):
        self.ensure_one()

    def action_open_face_registration_wizard(self):
        """
        Membuka wizard pendaftaran wajah untuk karyawan saat ini.
        """
        self.ensure_one()  # Pastikan metode dipanggil hanya pada satu record

        return {
            'name': "Daftarkan Wajah Karyawan",
            'type': 'ir.actions.act_window',
            'res_model': 'face_recognition.face_registration_wizard',  # Model wizard kita
            'view_mode': 'form',
            'target': 'new',  # Buka sebagai pop-up
            'context': {'default_employee_id': self.id},  # Kirim ID karyawan ke wizard
        }


from odoo import models, fields, api


class FaceRegistrationWizard(models.TransientModel):
    _name = 'face.registration.wizard'
    _description = 'Wizard for Employee Face Registration'

    employee_id = fields.Many2one('hr.employee', string="Karyawan", required=True, readonly=True)
    image_data_base64 = fields.Text(string="Gambar Wajah (Base64)")
    message = fields.Char(string="Status", readonly=True)
    camera_placeholder = fields.Char(string="Kamera", readonly=True)

    @api.model
    def default_get(self, fields):
        res = super(FaceRegistrationWizard, self).default_get(fields)
        # Ambil ID karyawan dari konteks (saat wizard dibuka dari form karyawan)
        if self._context.get('active_id') and self._context.get('active_model') == 'hr.employee':
            res['employee_id'] = self._context.get('active_id')
        return res

    def action_save_face(self):
        return {'type': 'ir.actions.act_window_close'}
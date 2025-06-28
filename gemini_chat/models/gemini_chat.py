from odoo import models, fields, api
import json
import logging
from odoo.exceptions import UserError
# import google.generativeai as genai
from google import genai

_logger = logging.getLogger(__name__)

class GeminiChat(models.Model):
    _name = 'gemini.chat'
    _inherit = ['mail.thread', 'mail.activity.mixin','api.abstract.mixin']
    _description = 'Gemini Chat'
    _order = 'create_date desc'

    name = fields.Char('Judul', required=True)
    question = fields.Text('Pertanyaan', required=True)
    answer = fields.Text('Jawaban', readonly=True)
    model = fields.Selection(
        [
            ('gemini-pro', 'Gemini Pro'),
            ('gemini-2.0-flash', 'Gemini 2.0 Flash'),
        ],
        string='Model',
        default='gemini-pro',
        required=True
    )
    user_id = fields.Many2one(
        'res.users',
        string='Pengguna',
        default=lambda self: self.env.user.id,
        readonly=True
    )

    @api.onchange('question')
    def _onchange_question(self):
        if self.question:
            response = self.send_to_gemini(self.question)
            print(f"Response Gemini (onchange): {response}")
            _logger.info(f"Response Gemini (onchange): {response}")
            # Ambil jawaban dari response, sesuaikan dengan struktur response API
            if isinstance(response, dict) and 'answer' in response:
                self.answer = response['answer']
            elif isinstance(response, dict) and 'text' in response:
                self.answer = response['text']
            else:
                self.answer = str(response)

    def send_to_gemini(self, message):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        response = self.call_external_api(
            url=url,
            method='POST',
        )
        print(f"send_to_gemini() called with message: {message}, got response: {response}")
        _logger.info(f"send_to_gemini() called with message: {message}, got response: {response}")
        return response

    @api.model
    def create(self, vals):
        if vals.get('question'):
            response = self.send_to_gemini(vals['question'])
            print(f"Response Gemini (create): {response}")
            _logger.info(f"Response Gemini (create): {response}")
            if isinstance(response, dict) and 'answer' in response:
                vals['answer'] = response['answer']
            elif isinstance(response, dict) and 'text' in response:
                vals['answer'] = response['text']
            else:
                vals['answer'] = str(response)
        return super(GeminiChat, self).create(vals)

    def write(self, vals):
        if 'question' in vals and vals['question']:
            response = self.send_to_gemini(vals['question'])
            print(f"Response Gemini (write): {response}")
            _logger.info(f"Response Gemini (write): {response}")
            if isinstance(response, dict) and 'answer' in response:
                vals['answer'] = response['answer']
            elif isinstance(response, dict) and 'text' in response:
                vals['answer'] = response['text']
            else:
                vals['answer'] = str(response)
        return super(GeminiChat, self).write(vals)

        # Metode untuk mendapatkan jawaban dari Gemini

    @api.model
    def _get_gemini_client(self):
        """Inisialisasi klien Gemini."""
        GEMINI_API_KEY = "AIzaSyC_"
        if not GEMINI_API_KEY:
            raise UserError("Gemini API Key tidak ditemukan. Harap konfigurasikan.")
        return genai.Client(api_key=GEMINI_API_KEY)

    def _generate_gemini_answer(self, model_name, question_text):
        """Memanggil API Gemini untuk mendapatkan jawaban."""
        client = self._get_gemini_client()
        try:
            response = client.models.generate_content(
                model=model_name,  # Menggunakan model yang dipilih di record
                contents=question_text,
            )
            return response.text
        except Exception as e:
            # Tangani error API dengan lebih baik di sini
            print(f"Error saat memanggil Gemini API: {e}")
            return f"Error: Gagal mendapatkan jawaban dari Gemini. ({e})"

    def action_get_answer(self):
        """Aksi yang akan dipanggil dari tombol atau otomatis."""
        self.ensure_one()  # Pastikan hanya satu record yang sedang diproses

        if not self.question:
            raise UserError("Pertanyaan tidak boleh kosong.")

        # Panggil fungsi untuk mendapatkan jawaban dari Gemini
        gemini_response = self._generate_gemini_answer(self.model, self.question)

        # Setel hasil respons ke kolom 'answer'
        self.answer = gemini_response
        print(f"Response Gemini: {gemini_response}")

        # Opsional: Jika Anda ingin menyimpan perubahan secara otomatis setelah aksi ini
        # self.flush(['answer'])

    # def action_ask_gemini(self):
    #     for rec in self:
    #         api_key = self.env['ir.config_parameter'].sudo().get_param('external_api_caller.bearer_token')
    #         if not api_key:
    #             raise UserError("API key Gemini belum disetel di sistem.")
    #
    #         genai.configure(api_key=api_key)
    #
    #         for rec in self:
    #             try:
    #                 model = genai.GenerativeModel(model_name=rec.model)
    #                 response = model.generate_content(rec.question)
    #                 rec.answer = response.text
    #                 _logger.info(f"Response from Gemini: {response.text}")
    #             except Exception as e:
    #                 _logger.error(f"Failed to generate content: {e}")
    #                 rec.answer = f"Error: {e}"

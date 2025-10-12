# -*- coding: utf-8 -*-
import logging
import google.generativeai as genai
import traceback
import sys
from odoo import api, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class GeminiMotivator(models.AbstractModel):
    """
    Model abstract untuk menampung logika cron job
    yang berinteraksi dengan Gemini AI.
    """
    _name = 'gemini.motivator'
    _description = 'Gemini Motivational Cron Job Logic'

    @api.model
    def _run_gemini_reminder_cron(self):
        """
        Metode ini dipanggil oleh cron job.
        Fungsinya: mengambil API key, memanggil Gemini, lalu mengirim email ke pengguna.
        """
        _logger.info("Starting Gemini Motivational Cron Job...")

        # 1. Ambil API Key dari System Parameters
        config_params = self.env['ir.config_parameter'].sudo()
        api_key = config_params.get_param('gemini.api_key')

        # DEBUG: print presence & masked key to help diagnosis
        try:
            print("DEBUG: gemini.api_key found?", bool(api_key))
            if api_key:
                masked = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "****"
                print(f"DEBUG: gemini.api_key (masked): {masked}")
            sys.stdout.flush()
        except Exception:
            # jangan ganggu flow jika printing gagal
            _logger.exception("Failed to print debug api_key info")

        if not api_key:
            _logger.warning("Gemini API Key not found in System Parameters (key: gemini.api_key). Cron job skipped.")
            return

        # 2. Konfigurasi dan Panggil Gemini AI
        try:
            print("DEBUG: configuring genai with provided API key...")
            sys.stdout.flush()
            genai.configure(api_key=api_key)

            # Prompt yang dirancang untuk menghasilkan pesan motivasi
            prompt = """
            Berikan satu kutipan motivasi singkat, nasihat karir, atau kata-kata penyemangat.
            Fokus pada tema seperti produktivitas, pengembangan diri, kepemimpinan, atau keseimbangan kerja-hidup.
            Pesan harus positif, inspiratif, dan tidak lebih dari 3 kalimat.
            Sampaikan dalam bahasa Indonesia yang formal namun menyentuh. jangan sama dengan sebelumnya
            """

            # coba model utama dulu (pakai model flash untuk akun free)
            tried_models = []
            success = False
            try:
                model_name = 'gemini-flash'
                tried_models.append(model_name)
                print(f"DEBUG: trying model {model_name}")
                sys.stdout.flush()
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                # ambil teks dari response dengan fallback
                try:
                    motivation_text = response.text.strip()
                except Exception:
                    motivation_text = str(response).strip()
                success = True
            except Exception as e_main:
                print("WARNING: primary model attempt failed:", e_main)
                traceback.print_exc()
                sys.stdout.flush()

                # coba dapatkan daftar model dari library untuk diagnosis
                models_list = None
                try:
                    list_func = getattr(genai, "list_models", None)
                    if callable(list_func):
                        try:
                            models_list = list_func()
                        except Exception as e_list:
                            print("DEBUG: genai.list_models() raised:", e_list)
                            traceback.print_exc()
                            sys.stdout.flush()
                except Exception:
                    pass

                # coba beberapa fallback model umum / varian flash
                fallback_models = ['gemini-flash-1', 'text-bison@001', 'chat-bison@001', 'text-bison', 'chat-bison']
                for fm in fallback_models:
                    try:
                        tried_models.append(fm)
                        print(f"DEBUG: trying fallback model {fm}")
                        sys.stdout.flush()
                        model = genai.GenerativeModel(fm)
                        response = model.generate_content(prompt)
                        try:
                            motivation_text = response.text.strip()
                        except Exception:
                            motivation_text = str(response).strip()
                        success = True
                        print(f"DEBUG: succeeded with fallback model {fm}")
                        sys.stdout.flush()
                        break
                    except Exception as e_fallback:
                        print(f"DEBUG: fallback model {fm} failed: {e_fallback}")
                        traceback.print_exc()
                        sys.stdout.flush()
                        continue

                # jika models_list ditemukan, tampilkan untuk membantu diagnosa
                if models_list is not None:
                    try:
                        print("DEBUG: available models (from genai.list_models()):")
                        print(repr(models_list))
                        sys.stdout.flush()
                    except Exception:
                        pass

            if not success:
                # berikan info pada log dan raise ValidationError agar Odoo menampilkan pesan yang jelas
                info_msg = f"Tried models: {tried_models}. See logs for full traceback and available models (if listed)."
                print("ERROR: All model attempts failed. " + info_msg)
                sys.stdout.flush()
                _logger.error("Failed to generate content from Gemini AI. " + info_msg)
                raise ValidationError(_("Gagal menghubungi Gemini AI atau model tidak tersedia. %s") % info_msg)

            _logger.info(f"Generated motivational text: {motivation_text}")

        except ValidationError:
            # re-raise ValidationError agar Odoo menangani pesan yang sudah jelas
            raise
        except Exception as e:
            # tampilkan traceback ke stdout agar terlihat di terminal
            print("ERROR: Unexpected exception when generating content from Gemini:", e)
            traceback.print_exc()
            sys.stdout.flush()
            _logger.error(f"Failed to generate content from Gemini AI: {e}")
            raise ValidationError(_("Gagal menghubungi Gemini AI. Pastikan API Key valid dan koneksi internet stabil. Error: %s") % e)

        # 3. Dapatkan template email
        template = self.env.ref('gemini_motivator.email_template_gemini_reminder', raise_if_not_found=False)
        if not template:
            _logger.error("Email template 'email_template_gemini_reminder' not found.")
            return

        # 4. Cari semua pengguna internal yang aktif dan punya email
        users_to_notify = self.env['res.users'].search([
            ('active', '=', True),
            ('share', '=', False),  # 'share=False' berarti pengguna internal
            ('email', '!=', False)
        ])
        
        if not users_to_notify:
            _logger.info("No active internal users with email found to send motivation.")
            return

        # 5. Kirim email ke setiap pengguna
        for user in users_to_notify:
            try:
                # Menggunakan with_context untuk meneruskan teks motivasi ke template
                email_context = {
                    'motivation_text': motivation_text,
                    'user_name': user.name,
                }
                template.with_context(email_context).send_mail(
                    user.id,
                    force_send=True,
                    email_layout_xmlid='mail.mail_notification_light' # Menggunakan layout email standar Odoo
                )
                _logger.info(f"Motivational email sent to {user.name} ({user.email})")
            except Exception as e:
                _logger.error(f"Failed to send email to {user.name}: {e}")

        _logger.info("Gemini Motivational Cron Job finished successfully.")
        return True
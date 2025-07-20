from odoo import models, fields, api
import requests
import base64
from odoo.exceptions import UserError

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    image_from_url = fields.Char(string='Image from URL')
    image_view_url = fields.Image(string='Image View URL', max_width=1920, max_height=1920)

    def _onchange_image_from_url(self):
        print("Image from URL changed:", self.image_from_url)
        if self.image_from_url:
            self.image_view_url = self._fetch_image_from_url(self.image_from_url)
        else:
            self.image_view_url = False

    def _fetch_image_from_url(self, url):
        print("Fetching image from URL:", url)
        try:
            response = requests.get(url, stream=True, timeout=5)
            response.raise_for_status()
            image_data = base64.b64encode(response.content)
            return image_data
        except requests.exceptions.RequestException as e:
            self.env.cr.rollback()  # Batalkan transaksi jika ada error
            raise UserError(f"Failed to fetch image from URL: {e}")

    def action_fetch_image_from_url(self):
        self.ensure_one()  # Pastikan metode ini dipanggil untuk satu record saja

        if not self.image_from_url:
            raise UserError("Please provide an Image URL first.")

        try:
            response = requests.get(self.image_from_url, stream=True, timeout=10)
            response.raise_for_status()  # Akan memicu HTTPError untuk status kode 4xx/5xx

            # Periksa Content-Type untuk memastikan itu gambar
            content_type = response.headers.get('Content-Type', '')
            if not content_type.startswith(('image/jpeg', 'image/png', 'image/gif')):
                raise UserError("The provided URL does not point to a valid image (JPEG, PNG, or GIF).")

            image_data = base64.b64encode(response.content)
            self.image_view_url = image_data

            # Pesan sukses (opsional, bisa juga dihilangkan)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': "Image fetched successfully!",
                    'type': 'success',
                    'sticky': False,
                }
            }

        except requests.exceptions.Timeout:
            raise UserError("Timeout: The server took too long to respond.")
        except requests.exceptions.ConnectionError:
            raise UserError(
                "Connection Error: Could not connect to the image URL. Please check your internet connection or the URL.")
        except requests.exceptions.HTTPError as e:
            raise UserError(
                f"HTTP Error: {e.response.status_code} - {e.response.reason}. Could not fetch image from URL.")
        except Exception as e:
            raise UserError(f"An unexpected error occurred: {e}")
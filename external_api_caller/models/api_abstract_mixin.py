from odoo import models, api
import requests
import logging

_logger = logging.getLogger(__name__)

class ExternalAPICallerMixin(models.AbstractModel):
    _name = 'api.abstract.mixin'
    _description = 'Mixin for External API Call'

    @api.model
    def call_external_api(self, url, method='GET', payload=None, custom_headers=None, timeout=10):
        token = self.env['ir.config_parameter'].sudo().get_param('external_api_caller.bearer_token')
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }

        if custom_headers:
            headers.update(custom_headers)

        try:
            _logger.info(f"[API CALL] {method} {url}")
            if payload:
                _logger.debug(f"[API PAYLOAD] {payload}")

            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=payload,
                timeout=timeout
            )

            _logger.info(f"[API RESPONSE] {response.status_code} - {response.text}")

            if response.status_code >= 400:
                return {
                    'error': f"HTTP {response.status_code}",
                    'details': response.text
                }

            return response.json()

        except requests.exceptions.Timeout:
            _logger.error("Request timed out")
            return {'error': 'Request timed out'}

        except requests.exceptions.RequestException as e:
            _logger.error(f"Request failed: {e}")
            return {'error': str(e)}

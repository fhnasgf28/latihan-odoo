from odoo import models, fields,api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    telegram_bot_token = fields.Char(string='Telegram Bot Token', config_parameter='gemini.telegram_bot_token')
    telegram_chat_id = fields.Char(string='Telegram Chat ID', config_parameter='gemini.telegram_chat_id')

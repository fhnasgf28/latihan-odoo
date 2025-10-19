from odoo import models, fields, api, _
from datetime import datetime
import logging
import requests
_logger = logging.getLogger(__name__)

class DailyJournal(models.Model):
    _name = 'daily.journal'
    _description = 'Daily Self Reflection Journal'
    _order = 'date desc'

    date = fields.Date(default=fields.Date.context_today, required=True)
    question = fields.Text(string='Reflection Question')
    answer = fields.Text(string='User Answer')
    mood = fields.Selection([
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative')
    ], string='Mood Analysis')
    ai_insight = fields.Text(string='AI Insight',  readonly=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)
    telegram_chat_id = fields.Char(string='Telegram Chat ID', help='Chat ID where question was sent')

    @api.model
    def _get_default_question(self):
        return (
            "📔 *Daily Reflection*\n"
            "1. Apa hal terbaik yang terjadi hari ini?\n"
            "2. Apa yang ingin kamu syukuri?\n"
            "3. Apa pelajaran penting hari ini?\n\n"
            "Silakan balas pesan ini untuk menjawab."
        )

    @api.model
    def send_daily_reflection(self):
        users = self.env['res.users'].search([('telegram_chat_id', '!=', False)])
        print(users)
        if not users:
            _logger.warning("No users found with Telegram chat ID. Daily reflection not sent.")
            return True
        for user in users:
            question = self._get_default_question()
            journal = self.create({
                'user_id': user.id,
                'telegram_chat_id': user.telegram_chat_id,
                'question': question,
                'date': fields.Date.context_today(self),
            })
            sent = False
            try:
                bot = self.env['telegram.bot']
                if bot:
                    bot.send_message(chat_id=user.telegram_chat_id,text=question, parse_mode='Markdown')
                    sent = True
            except Exception:
                _logger.error("Failed to send daily reflection to Telegram")
            if not sent:
                self._send_telegram_direct(user.telegram_chat_id, question)
        return True

    def _send_telegram_direct(self, chat_id, text):
        token = self.env['ir.config_parameter'].sudo().get_param('gemini.telegram_bot_token')
        if not token:
            _logger.warning("Telegram token not configured in ir.config_parameter (odoo_gemini.telegram_token).")
            return False
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            resp = requests.post(url, json={
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'Markdown'
            }, timeout=10)
            resp.raise_for_status()
            return True
        except Exception as e:
            _logger.error(f"Failed to send daily reflection to Telegram: {str(e)}")
            return False

    @api.model
    def receive_telegram_reply(self, chat_id, text):
        user = self.env['res.users'].search([('telegram_chat_id', '=', str(chat_id))], limit=1)
        journal = self.search([
            ('telegram_chat_id', '=', str(chat_id)),
            ('answer', '=', False)
        ], order='date desc, id desc', limit=1)
        if not journal:
            journal = self.create({
                'question': 'User reply (no open question found)',
                'user_id': user.id if user else False,
                'telegram_chat_id': str(chat_id),
                'answer': text,
                'date': fields.Date.context_today(self),
            })
            journal.answer = text
            self._analyze_with_gemini(journal.id)
            return True

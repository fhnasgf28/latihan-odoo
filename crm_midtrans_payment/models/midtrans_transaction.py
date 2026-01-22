import base64
import json
import requests

from odoo import api, fields,models, _
from odoo.exceptions import ValidationError, UserError

class CrmMidtransTransaction(models.Model):
    _name = 'crm.midtrans.transaction'
    _description = 'crm midtrans transaction'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string="Midtrans Order ID", required=True, readonly=True, copy=False, index=True)
    lead_id = fields.Many2one("crm.lead", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one("res.company", related="lead_id.company_id", store=True, readonly=True)
    currency_id = fields.Many2one("res.currency", related="lead_id.company_currency_id", store=True, readonly=True)
    amount = fields.Monetary(required=True)
    snap_token = fields.Char(readonly=True, copy=False)
    snap_redirect_url = fields.Char(readonly=True, copy=False)
    transaction_status = fields.Char(readonly=True, tracking=True)
    fraud_status = fields.Char(readonly=True, tracking=True)
    payment_type = fields.Char(readonly=True)
    status_code = fields.Char(readonly=True)
    gross_amount = fields.Char(readonly=True)
    raw_notification = fields.Text(readonly=True)
    last_notification_at = fields.Datetime(readonly=True)
    last_fingerprint = fields.Char(readonly=True, copy=False)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending", "Pending"),
            ("paid", "Paid"),
            ("failed", "Failed"),
            ("expired", "Expired"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        tracking=True,
        required=True,
    )

    def _get_midtrans_environment(self):
        return self.env["ir.config_parameter"].sudo().get_param("crm_midtrans_payment.midtrans_environment", "sandbox")

    def _get_midtrans_server_key(self):
        key = self.env["ir.config_parameter"].sudo().get_param("crm_midtrans_payment.midtrans_server_key")
        if not key:
            raise ValidationError(_("Midtrans Server Key is not configured"))
        return key

    def _snap_base_url(self):
        env = self._get_midtrans_environment()
        return "https://app.sandbox.midtrans.com" if env == "sandbox" else "https://app.midtrans.com"

    def _midtrans_auth_header(self):
        server_key = self._get_midtrans_server_key()
        raw = f"{server_key}:".encode("utf-8")  # password empty :contentReference[oaicite:4]{index=4}
        return "Basic " + base64.b64encode(raw).decode("utf-8")

    def action_open_snap(self):
        self.ensure_one()
        if not self.snap_redirect_url:
            raise UserError(_("Snap redirect URL is empty. Generate payment link first."))
        return {
            "type": "ir.actions.act_url",
            "url": self.snap_redirect_url,
            "target": "new",
        }

    def action_refresh_status(self):
        self.ensure_one()
        url = f"{self._snap_base_url()}/v2/{self.name}/status"
        headers = {
            "Accept": "application/json",
            "Authorization": self._midtrans_auth_header(),
        }
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code >= 400:
            raise UserError(_("Midtrans status request failed: %s") %resp.text)
        data = resp.json()
        fingerprint = f"{data.get('transaction_status')}|{data.get('fraud_status')}|{data.get('status_code')}|{data.get('gross_amount')}"
        self._apply_midtrans_notification(data, fingerprint=fingerprint)

    def _apply_midtrans_notification(self, payload, fingerprint=None):
        self.ensure_one()
        tx_status = payload.get("transaction_status")
        fraud_status = payload.get("fraud_status")
        status_code = payload.get("status_code", "")
        new_state = self.state
        if tx_status in ("settlement",):
            new_state = "paid"
        elif tx_status == 'capture':
            new_state = "paid" if (fraud_status or "").lower() == "accept" else "pending"
        elif tx_status in ("pending",):
            new_state = "pending"
        elif tx_status in ("expire", ):
            new_state = "expired"
        elif tx_status in ("cancel", ""):
            new_state = "cancelled"
        elif tx_status in ("deny", "failure"):
            new_state = "failed"

        self.write(
            {
                "transaction_status": tx_status,
                "fraud_status": fraud_status,
                "payment_type": payload.get("payment_type"),
                "status_code": status_code,
                "gross_amount": str(payload.get("gross_amount", "")),
                "raw_notification": json.dumps(payload, indent=2, ensure_ascii=False),
                "last_notification_at": fields.Datetime.now(),
                "state": new_state,
                "last_fingerprint": fingerprint or self.last_fingerprint,
            }
        )
        self.message_post(body=_("Midtrans webhook/status update: %s (fraud=%s)") % (tx_status, fraud_status))
        if new_state == "paid":
            self.lead_id._action_set_won_from_midtrans(self)

    @api.model
    def create_snap_transaction(self, lead, amount):
        if amount <= 0:
            raise UserError(_("Amount must be greater than 0"))
        order_id = self.env['ir.sequence'].next_by_code('crm.midtrans.tx') or f"MTX-{lead.id}"
        tx = self.create(
            {
                "name": order_id,
                "lead_id": lead.id,
                "amount": amount,
                "state": "draft",
            }
        )
        url = f"{tx._snap_base_url()}/snap/v1/transactions"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application",
            "Authorization": tx._midtrans_auth_header(),
        }
        payload = {
            "transaction_details": {
                "order_id": order_id,
                "gross_amount": int(round(amount)),
            },
            "customer_details": {
                "first_name": (lead.partner_name or lead.contact_name or lead.name or "Customer")[:255],
                "email": lead.email_from or "",
                "phone": lead.phone or lead.mobile or "",
            },
            # (optional) callbacks: if you have a public return URL
            # "callbacks": {"finish": "https://yourdomain/some/thankyou"},
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if resp.status_code >= 400:
            raise UserError(_("Midtrans Snap request failed (%s): %s") % (resp.status_code, resp.text))

        data = resp.json()
        tx.write(
            {
                "snap_token": data.get("token"),
                "snap_redirect_url": data.get("redirect_url"),
                "state": "pending",
            }
        )
        tx.message_post(body=_("Snap created. Redirect URL stored."))

        return tx



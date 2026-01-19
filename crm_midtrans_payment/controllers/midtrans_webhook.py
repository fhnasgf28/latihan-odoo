import json
import hashlib
from odoo import http
from odoo.http import request

class MidtransWebhookController(http.Controller):
    @http.route("/midtrans/webhook", type="http", auth="public", methods=["POST"], csrf=False)
    def midtrans_webhook(self, **kwargs):
        payload_raw = request.httprequest.data or b"{}"
        try:
            payload = json.loads(payload_raw.decode("utf-8"))
        except Exception:
            return request.make_response("invalid json", status=400)

        order_id = payload.get("order_id")
        status_code = str(payload.get("status_code", ""))
        gross_amount = str(payload.get("gross_amount", ""))
        signature_key = payload.get("signature_key", "")
        if not order_id:
            return request.make_response("Missing order_id", status=400)
        # find transaction
        Tx = request.env['crm.midtrans.transaction'].sudo()
        tx = Tx.search(["name", "=", order_id], limit=1)
        if not tx:
            return request.make_response("OK", status=200)

        # verivy signature
        server_key = tx._get_midtrans_server_key()
        expected = hashlib.sha512(f"{order_id}{status_code}{gross_amount}{server_key}".encode("utf-8")).hexdigest()
        if not signature_key or signature_key.lower() != expected.lower():
            tx.message_post(body="Webhook rejected: invalid signature_key")
            return request.make_response("invalid signature", status=401)
        fingerprint = f"{payload.get('transaction_status')}|{payload.get('fraud_status')}|{status_code}|{gross_amount}"
        if tx.last_fingerprint and tx.last_fingerprint == fingerprint:
            return request.make_response("ok", status=200)
        tx.sudo()._apply_midtrans_notification(payload, fingerprint=fingerprint)
        return request.make_response("ok", status=200)



from odoo import api, fields, models,_
from odoo.exceptions import ValidationError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    midtrans_tx_ids = fields.One2many('crm.midtrans.transaction', 'lead_id', string='Midtrans Transactions')
    midtrans_tx_count = fields.Integer(compute='_compute_midtrans_tx_count', string='Midtrans Transactions Count')
    midtrans_last_payment_state = fields.Selection(
        related="midtrans_tx_ids.state", string="Last Payment State", readonly=True
    )

    def _compute_midtrans_tx_count(self):
        for lead in self:
            lead.midtrans_tx_count = len(lead.midtrans_tx_ids)

    def action_view_midtrans_transactions(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Midtrans Transactions"),
            "res_model": "crm.midtrans.transaction",
            "view_mode": "tree,form",
            "domain": [("lead_id", "=", self.id)],
            "context": {"default_lead_id": self.id},
        }

    def action_generate_midtrans_payment_link(self):
        self.ensure_one()
        if self.type != "opportunity":
            raise ValidationError(_("Only opportunities can generate Midtrans payment links."))
        amount = self.expected_revenue or 0.0
        if amount <= 0:
            raise ValidationError(_("Expected Revenue must be set (> 0) to generate payment link."))

        tx = self.env["crm.midtrans.transaction"].create_snap_transaction(self, amount)
        return tx.action_open_snap()

    def _action_set_won_from_midtrans(self, tx):
        self.ensure_one()
        if self.type != "opportunity":
            return
        Stage = self.env['crm.stage'].sudo()
        domain = [("is_won", "=", True)]
        if self.team_id:
            team_stage = Stage.search(domain + [('team_id', '=', self.team_id.id)], limit=1)
            stage = team_stage or Stage.serch(domain + [("team_id", "=", False)], limit=1)
        else:
            stage = Stage.search(domain + [("team_id", "=", False)], limit=1)

        vals = {"probability": 100.0}
        if stage:
            vals["stage_id"] = stage.id
        self.write(vals)
        self.message_post(body=_("Marked as Won due to successful midtrans payment"))
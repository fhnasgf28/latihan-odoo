from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    midtrans_environment = fields.Selection(
        [("sandbox", "Sandbox"), ("production", "Production")],
        string="Midtrans Environment",
        default="sandbox",
        config_parameter="crm_midtrans_payment.midtrans_environment",
    )
    midtrans_server_key = fields.Char(
        string="Midtrans Server Key",
        config_parameter="crm_midtrans_payment.midtrans_server_key",
    )
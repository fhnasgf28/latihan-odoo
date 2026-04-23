from odoo import models, fields, api, _

class SalesConfigSettings(models.Model):
    _name = 'sales.config.settings'
    _description = 'Sales Approval Configuration'

    name = fields.Char(string="Name", default="Sales Approval Settings", readonly=True)
    company_id = fields.Many2one(
        'res.company', 
        string="Company", 
        required=True, 
        default=lambda self: self.env.company
    )
    
    # --- Fitur Approval ---
    is_approval_active = fields.Boolean(
        string="Enable Sales Approval Matrix", 
        default=True,
        help="Aktifkan atau nonaktifkan seluruh alur approval matrix."
    )
    
    approval_type = fields.Selection([
        ('parallel', 'Parallel (Anyone can approve anytime)'),
        ('sequential', 'Sequential (Must follow sequence/level)')
    ], string="Approval Method", default='parallel', required=True)

    allow_self_approval = fields.Boolean(
        string="Allow Self Approval", 
        default=False,
        help="Jika aktif, pembuat Sales Order yang juga seorang approver bisa meng-approve order miliknya sendiri."
    )

    # --- Notifikasi ---
    notify_via_email = fields.Boolean(string="Notify Approvers via Email", default=True)
    notify_via_chatter = fields.Boolean(string="Post Progress to Chatter", default=True)

    # --- Batasan ---
    lock_so_on_to_approve = fields.Boolean(
        string="Lock SO on To Approve", 
        default=True,
        help="Jika aktif, user tidak bisa mengedit baris order saat status sedang 'To Approve'."
    )

    _sql_constraints = [
        ('company_uniq', 'unique (company_id)', 'The configuration must be unique per company !'),
    ]

    def action_open_settings(self):
        # Helper untuk membuka record setting yang sudah ada (singleton)
        setting = self.search([('company_id', '=', self.env.company.id)], limit=1)
        if not setting:
            setting = self.create({'company_id': self.env.company.id})
        
        return {
            'name': _('Sales Approval Settings'),
            'type': 'ir.actions.act_window',
            'res_model': 'sales.config.settings',
            'view_mode': 'form',
            'res_id': setting.id,
            'target': 'current',
        }

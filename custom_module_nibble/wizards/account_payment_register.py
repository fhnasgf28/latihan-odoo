from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    bank_charge = fields.Monetary(
        string="Bank Charge",
        default=0.0,
        help="Bank fees deducted from total payments."
    )

    bank_charge_account_id = fields.Many2one(
        'account.account',
        string="Bank Charge Account",
        help="Accounts that will be used to record bank costs."
    )

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)

        if self.bank_charge > 0:
            if not self.bank_charge_account_id:
                raise UserError(_("Please select a Bank Expense Account first."))
            if self.bank_charge >= self.amount:
                raise UserError(_("Bank charges cannot be greater than or equal to the payment amount."))

            payment_vals['amount'] = self.amount - self.bank_charge
            payment_vals['write_off_line_vals'] = [
                {
                    'name': _('Bank Charge'),
                    'account_id': self.bank_charge_account_id.id,
                    'balance': self.bank_charge,
                    'amount_currency': self.bank_charge,
                },
            ]

        return payment_vals

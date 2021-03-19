# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class SmsHistory(models.Model):

    _name = "sms.history"
    _description = "SMS History"

    contact_to = fields.Char('To:')
    template_body = fields.Text('Message:', translate=True, sanitize=False)
    status = fields.Char('Status')
    account_gateway = fields.Selection([('msg91','MSG91'),
                                        ('clicksend','ClickSend'),
                                        ('textlocal','TextLocal')], string="SMS Gateway")
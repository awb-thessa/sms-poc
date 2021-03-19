# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class AccountSmsTemplate(models.Model):

    _name = "account.sms.template"
    _description = "SMS Template"

    name = fields.Char(required=True, string='Template Name', translate=True)
    template_body = fields.Text('Body', translate=True, sanitize=False)
    global_temp = fields.Boolean('Global', default=True)
    model_id = fields.Many2one('ir.model', 'Applies To')
    condition = fields.Selection([('order_placed','Order Placed'),
                                  ('order_confirmed','Order Confirmed'),
                                  ('order_delivered','Order Delivered'),
                                  ('invoice_validate','Invoice Validate'),
                                  ('invoice_paid','Invoice Paid'),
                                  ('order_cancelled','Order Cancelled')], 'Condition')
    account_gateway = fields.Selection([('msg91','MSG91'),
                                        ('clicksend','ClickSend'),
                                        ('textlocal','TextLocal')], string="SMS Gateway")

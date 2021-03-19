# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError
import http
import json

import urllib.request
import urllib.parse

import logging
_logger = logging.getLogger(__name__)

try:
    import clicksend_client
    from clicksend_client import SmsMessage
    from clicksend_client.rest import ApiException
except ImportError :
    _logger.debug('Cannot `import clicksend_client` please run this command: sudo pip3 install clicksend_client')

class AccountMove(models.Model):
    _inherit = 'account.move'


    def action_post(self):
        result = super(AccountMove, self).action_post()
        for invoice in self:
            template_id = self.env['account.sms.template'].search([('model_id.model','=', invoice._name),
                                                           ('condition','=', 'invoice_validate'),
                                                           ('global_temp','=', False)], limit=1)
            if not template_id.account_gateway:
                UserError(_('Please Set Account Gateway In Template For Sending SMS.'))
            if template_id.account_gateway == 'msg91':
                conn = http.client.HTTPSConnection("api.msg91.com")
                configuration_id = self.env['sms.account.configuration'].\
                                search([('account_gateway','=', template_id.account_gateway)], limit=1)
                access_token = configuration_id.msg_authkey
                msg_route = configuration_id.msg_route
                msg_sender = configuration_id.msg_sender
                template_body = template_id.template_body
                msg_country_code = configuration_id.msg_country_code
                if invoice.partner_id.mobile:
                    payload = "{ \"sender\": \"%s\", \"route\": \"%s\", \"country\": \"%s\", \"sms\": [ { \"message\": \"%s\", \"to\": [ \"%s\"] } ] }" %\
                                (msg_sender, msg_route, msg_country_code, template_body, invoice.partner_id.mobile)
                    headers = {'authkey': access_token,'content-type': "application/json"}
                    conn.request("POST", "/api/v2/sendsms?country=91", payload, headers)
                    res = conn.getresponse()
                    data = res.read()
                    json.loads(data.decode("utf-8"))
                else:
                    UserError(_('Member Mobile Number Does Not Added'))
            elif template_id.account_gateway == 'clicksend':
                configuration_id = self.env['sms.account.configuration'].\
                                search([('account_gateway','=', template_id.account_gateway)], limit=1)
                configuration = clicksend_client.Configuration()
                configuration.username = configuration_id.clicksend_username
                configuration.password = configuration_id.clicksend_apikey
                template_body = template_id.template_body
                if invoice.partner_id.mobile:
                    api_instance = clicksend_client.SMSApi(clicksend_client.ApiClient(configuration))
                    sms_message = SmsMessage(source="php", body=template_body, to=invoice.partner_id.mobile)
                    sms_messages = clicksend_client.SmsMessageCollection(messages=[sms_message])
                    try:
                        api_instance.sms_send_post(sms_messages)
                    except ApiException as e:
                        UserError(_("Exception when calling SMSApi->sms_send_post: %s\n" % e))
                else:
                    UserError(_('Member Mobile Number Does Not Added'))
            elif template_id.account_gateway == 'textlocal':
                configuration_id = self.env['sms.account.configuration'].\
                                search([('account_gateway','=', template_id.account_gateway)], limit=1)
                textlocal_authkey = configuration_id.textlocal_authkey
                textlocal_sender = configuration_id.textlocal_sender
                template_body = template_id.template_body
                if invoice.partner_id.mobile:
                    sms_messages =  urllib.parse.urlencode({'apikey': textlocal_authkey, 'numbers': invoice.partner_id.mobile,
                        'message' : template_body, 'sender': textlocal_sender})
                    sms_messages = sms_messages.encode('utf-8')
                    sms_request = urllib.request.Request("https://api.textlocal.in/send/?")
                    api_responses = urllib.request.urlopen(sms_request, sms_messages)
                    api_response = json.loads(api_responses.read())
                else:
                    UserError(_('Member Mobile Number Does Not Added'))
        return result

    def action_invoice_register_payment(self):
        result = super(AccountPayment, self).action_invoice_register_payment()
        for payment in self:
            template_id = self.env['account.sms.template'].search([('model_id.model','=', payment._name),
                                                           ('condition','=', 'invoice_paid'),
                                                           ('global_temp','=', False)], limit=1)
            if not template_id.account_gateway:
                UserError(_('Please Set Account Gateway In Template For Sending SMS.'))
            if template_id.account_gateway == 'msg91':
                conn = http.client.HTTPSConnection("api.msg91.com")
                configuration_id = self.env['sms.account.configuration'].\
                                search([('account_gateway','=', template_id.account_gateway)], limit=1)
                access_token = configuration_id.msg_authkey
                msg_route = configuration_id.msg_route
                msg_sender = configuration_id.msg_sender
                template_body = template_id.template_body
                msg_country_code = configuration_id.msg_country_code
                if payment.partner_id.mobile:
                    payload = "{ \"sender\": \"%s\", \"route\": \"%s\", \"country\": \"%s\", \"sms\": [ { \"message\": \"%s\", \"to\": [ \"%s\"] } ] }" %\
                                (msg_sender, msg_route, msg_country_code, template_body, payment.partner_id.mobile)
                    headers = {'authkey': access_token,'content-type': "application/json"}
                    conn.request("POST", "/api/v2/sendsms?country=91", payload, headers)
                    res = conn.getresponse()
                    data = res.read()
                    json.loads(data.decode("utf-8"))
                else:
                    UserError(_('Member Mobile Number Does Not Added'))
            elif template_id.account_gateway == 'clicksend':
                configuration_id = self.env['sms.account.configuration'].\
                                search([('account_gateway','=', template_id.account_gateway)], limit=1)
                configuration = clicksend_client.Configuration()
                configuration.username = configuration_id.clicksend_username
                configuration.password = configuration_id.clicksend_apikey
                template_body = template_id.template_body
                if payment.partner_id.mobile:
                    api_instance = clicksend_client.SMSApi(clicksend_client.ApiClient(configuration))
                    sms_message = SmsMessage(source="php", body=template_body, to=payment.partner_id.mobile)
                    sms_messages = clicksend_client.SmsMessageCollection(messages=[sms_message])
                    try:
                        api_instance.sms_send_post(sms_messages)
                    except ApiException as e:
                        UserError(_("Exception when calling SMSApi->sms_send_post: %s\n" % e))
                else:
                    UserError(_('Member Mobile Number Does Not Added'))
            elif template_id.account_gateway == 'textlocal':
                configuration_id = self.env['sms.account.configuration'].\
                                search([('account_gateway','=', template_id.account_gateway)], limit=1)
                textlocal_authkey = configuration_id.textlocal_authkey
                textlocal_sender = configuration_id.textlocal_sender
                template_body = template_id.template_body
                if payment.partner_id.mobile:
                    sms_messages =  urllib.parse.urlencode({'apikey': textlocal_authkey, 'numbers': payment.partner_id.mobile,
                        'message' : template_body, 'sender': textlocal_sender})
                    sms_messages = sms_messages.encode('utf-8')
                    sms_request = urllib.request.Request("https://api.textlocal.in/send/?")
                    api_responses = urllib.request.urlopen(sms_request, sms_messages)
                    api_response = json.loads(api_responses.read())
                else:
                    UserError(_('Member Mobile Number Does Not Added'))
        return result

# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import http
import yaml

import logging
_logger = logging.getLogger(__name__)

try:
    import clicksend_client
    from clicksend_client.rest import ApiException
except ImportError :
    _logger.debug('Cannot `import clicksend_client` please run this command: sudo pip3 install clicksend_client')

import urllib.request
import urllib.parse

import json


class SmsAccountConfiguration(models.Model):

    _name = "sms.account.configuration"
    _description = "SMS Account Configuration"

    name = fields.Char(string='Account Name')
    priority = fields.Integer('Priority')
    msg_authkey = fields.Char('MSG Authentication Key')
    msg_route = fields.Char('MSG Route', default='4', size=1, help="""Eg: route=1 for promotional,
                                                                        route=4 for transactional SMS""")
    msg_sender = fields.Char('MSG Sender', size=6, help="""Receiver will see this as sender's ID""")
    msg_country_code = fields.Char('MSG Country Code', help="""0 for international, 1 for USA, 91 for India""")
    account_gateway = fields.Selection([('msg91','MSG91'),('clicksend','ClickSend'),('textlocal','TextLocal')], string="SMS Gateway")

    clicksend_username = fields.Char('ClickSend Username')
    clicksend_apikey = fields.Char('ClickSend API Key')
    active = fields.Boolean(default=True)

    textlocal_authkey = fields.Char('TextLocal Authentication Key')
    textlocal_sender = fields.Char('TextLocal Sender', size=6, help="""Receiver will see this as sender's ID""", default='TXTLCL')


    def action_test_connection(self):
        for order in self:
            if order.account_gateway == 'msg91': 
                conn = http.client.HTTPSConnection("api.msg91.com")
                access_token = order.msg_authkey
                conn.request("GET", "/api/validate.php?authkey=%s" % access_token)
                res = conn.getresponse()
                data = res.read()
                record_dict = data.decode("utf-8")
                if record_dict == 'Valid':
                    raise UserError(_('Test Connection Successfully!.'))
                else:
                    raise UserError(_('Wrong Authentication Key!.'))
            elif order.account_gateway == 'clicksend':
                configuration = clicksend_client.Configuration()
                configuration.username = order.clicksend_username
                configuration.password = order.clicksend_apikey
                api_instance = clicksend_client.AccountApi(clicksend_client.ApiClient(configuration))
                try:
                    api_response = yaml.load(api_instance.account_get())
                    if api_response.get('response_code') == 'SUCCESS':
                        raise UserError(_('Test Connection Successfully!.'))
                    else:
                        raise UserError(_('Wrong Username & Authentication Key!.'))
                except ApiException as e:
                    raise UserError("Exception when calling AccountApi->account_get: %s\n" % e)
            elif order.account_gateway == 'textlocal': 
               
                req = urllib.request.Request('https://messagingsuite.smart.com.ph/cgphttp/servlet/sendmsg?destination=63950467975&text=TestMessage+AccounConfig+SMSGatewayOdoo', method="POST")
                req.add_header('Authorization', 'Basic amVycnkubWFycXVlc2VzQG1hbmRhbGF5LmNvbS5waDpwNGpOZ0w5Uw==')
                req.add_header('Content-Type', 'application/json')
                data = { "hello": "world" }
                data = json.dumps(data)
                data = data.encode()
                f = urllib.request.urlopen(req, data=data)
                content = f.read()
                print(content)
                
                resp, code = (f.read(), f.code)
                api_response = yaml.load(resp)
                if api_response.get('status') == 'success':
                    raise UserError(_('Test Connection Successfully!.'))
                else:
                    raise UserError(_('Wrong Authentication Key!.'))

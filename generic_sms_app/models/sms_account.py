# -*- coding: utf-8 -*-

from odoo import models, fields, api, sql_db, _
from odoo.exceptions import UserError
import http
import json
import ast
import yaml

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


class SmsAccount(models.Model):

    _name = "sms.account"
    _description = "SMS"

    user_id = fields.Many2one(
        'res.users', 'Assigned to',
        default=lambda self: self.env.user,
        index=True, required=True)
    name = fields.Char('Name',default=lambda self: _('New'))
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent','Sent'),
        ('cancel','Cancel'),
        ], string='State', default='draft')
    mobile_no = fields.Char('Contact No')
    account_id = fields.Many2one('sms.account.configuration', 'SMS Gateway')
    template_id = fields.Many2one('account.sms.template', 'Template', domain=[('global_temp','=',True)])
    template_body = fields.Text('Message', translate=True,
                                help="Template Body")
    send_sms_type = fields.Selection([
        ('group', 'Campaigns'),
        ('multi_member','Multiple Members'),
        ('individual_member','Individual Member/Number'),
        ], string='Send SMS Type')
    group_id = fields.Many2one('sms.groups', 'SMS Campaigns')
    member_ids = fields.Many2many('res.partner', 'sms_account_res_partner_rel', string='Contacts')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('sms.account') or _('New')
        return super(SmsAccount, self).create(vals)


    def unlink(self):
        for order in self:
            if order.state not in ('draft', 'cancel'):
                raise UserError(_('You cannot delete an invoice which is not draft or cancelled. You should create a credit note instead.'))
        return super(SmsAccount, self).unlink()


    def action_draft(self):
        return self.write({'state': 'draft'})


    def action_cancel(self):
        return self.write({'state': 'cancel'})


    def action_sms_confirm(self):
        for order in self:
            if order.account_id.account_gateway == 'msg91':
                conn = http.client.HTTPSConnection("api.msg91.com")
                access_token = order.account_id.msg_authkey
                msg_route = order.account_id.msg_route
                msg_sender = order.account_id.msg_sender
                template_body = order.template_body
                msg_country_code = order.account_id.msg_country_code
                msg_group_name = order.group_id.name
                if order.send_sms_type == 'individual_member':
                    payload = "{ \"sender\": \"%s\", \"route\": \"%s\", \"country\": \"%s\", \"sms\": [ { \"message\": \"%s\", \"to\": [ \"%s\"] } ] }" %\
                                (msg_sender, msg_route, msg_country_code, template_body, order.mobile_no)
                    headers = {'authkey': access_token,'content-type': "application/json"}
                    conn.request("POST", "/api/v2/sendsms?country=91", payload, headers)
                    res = conn.getresponse()
                    data = res.read()
                    record_dict = json.loads(data.decode("utf-8"))
                    if record_dict.get('type') == 'success':
                        order.state = 'sent'
                elif order.send_sms_type == 'group':
                    if not order.group_id.active:
                        message =  '"' + order.group_id.name + '"' + ' ' + "Was Deactive !. Please Active Groups"
                        raise UserError(_(message))
                    # Create Group
                    payload = "{ \"group_name\": \"%s\"}" % (msg_group_name)
                    conn.request("GET", "/api/add_group.php?group_name=%s&authkey=%s" % (msg_group_name, access_token))
                    res = conn.getresponse()
                    data = res.read()
                    record_dict = json.loads(data.decode("utf-8"))
                    msg_group_id = record_dict.get('grpId')
                    order.group_id.mg_cont_group_id = msg_group_id 
                    if record_dict.get('msgType') == 'success':
                        # Added member In Group
                        for member in order.group_id.member_ids:
                            if not member.mobile:
                                raise UserError(_('Member Mobile Number Does Not Added'))
                            if member.mobile:
                                conn.request("GET", "/api/add_contact.php?group=%s&mob_no=%s&name=%s&authkey=%s" %\
                                             (msg_group_id, member.mobile, member.name, access_token))
                                member_result = conn.getresponse()
                                member_data = member_result.read()
                                member_dict = json.loads(member_data.decode("utf-8"))
                                if member_dict.get('msg_type') == 'success':
                                    # Send Message To Member
                                    memberload = "{ \"sender\": \"%s\", \"route\": \"%s\", \"country\": \"%s\", \"sms\": [ { \"message\": \"%s\", \"to\": [ \"%s\"] } ] }" %\
                                                (msg_sender, msg_route, msg_country_code, template_body, member.mobile)
                                    memberheaders = {'authkey': access_token,'content-type': "application/json"}
                                    conn.request("POST", "/api/v2/sendsms?country=91", memberload, memberheaders)
                                    messageres = conn.getresponse()
                                    messagedata = messageres.read()
                                    json.loads(messagedata.decode("utf-8"))
                        order.state = 'sent'
                    elif record_dict.get('msgType') == 'error':
                        message = record_dict.get('msg')
                        raise UserError(_(message))
                elif order.send_sms_type == 'multi_member':
                    conn = http.client.HTTPSConnection("api.msg91.com")
                    access_token = order.account_id.msg_authkey
                    msg_route = order.account_id.msg_route
                    msg_sender = order.account_id.msg_sender
                    template_body = order.template_body
                    msg_country_code = order.account_id.msg_country_code
                    for member in order.member_ids:
                        if not member.mobile:
                            raise UserError(_('Member Mobile Number Does Not Added'))
                        if member.mobile:
                            payload = "{ \"sender\": \"%s\", \"route\": \"%s\", \"country\": \"%s\", \"sms\": [ { \"message\": \"%s\", \"to\": [ \"%s\"] } ] }" %\
                                        (msg_sender, msg_route, msg_country_code, template_body, member.mobile)
                            headers = {'authkey': access_token,'content-type': "application/json"}
                            conn.request("POST", "/api/v2/sendsms?country=91", payload, headers)
                            res = conn.getresponse()
                            data = res.read()
                            record_dict = json.loads(data.decode("utf-8"))
                            if record_dict.get('type') == 'success':
                                order.state = 'sent'
            elif order.account_id.account_gateway == 'clicksend':
                configuration = clicksend_client.Configuration()
                configuration.username = order.account_id.clicksend_username
                configuration.password = order.account_id.clicksend_apikey
                template_body = order.template_body
                # Group Name
                msg_group_name = order.group_id.name
                if order.send_sms_type == 'individual_member':
                    api_instance = clicksend_client.SMSApi(clicksend_client.ApiClient(configuration))
                    sms_message = SmsMessage(source="php", body=template_body, to=order.mobile_no)
                    sms_messages = clicksend_client.SmsMessageCollection(messages=[sms_message])
                    api_response = ast.literal_eval(api_instance.sms_send_post(sms_messages))
                    if api_response.get('response_code') == 'SUCCESS':
                        order.state = 'sent'
                elif order.send_sms_type == 'group':
                    if not order.group_id.active:
                        message =  '"' + order.group_id.name + '"' + ' ' + "Was Deactive !. Please Active Groups"
                        raise UserError(_(message))
                    # Create Group
                    check_mobile_no = all([x.mobile for x in order.group_id.member_ids])
                    if not check_mobile_no:
                        raise UserError(_('Member Mobile Number Does Not Added'))

                    # Create Contact List Name
                    contact_list_api_instance = clicksend_client.ContactListApi(clicksend_client.ApiClient(configuration))
                    list_name = clicksend_client.List(list_name=msg_group_name)
                    api_response = ast.literal_eval(contact_list_api_instance.lists_post(list_name))
                    api_response_data = api_response.get('data')
                    list_id = api_response_data.get('list_id')
                    # Set List Number In Group
                    order.group_id.mg_cont_group_id = list_id 
                    # create an instance of the API class
                    contact_api_instance = clicksend_client.ContactApi(clicksend_client.ApiClient(configuration))
                    smsapi_instance = clicksend_client.SMSApi(clicksend_client.ApiClient(configuration))
                    for member in order.group_id.member_ids:
                        # Sending SMS
                        if not member.mobile:
                            raise UserError(_('Member Mobile Number Does Not Added'))
                        if member.mobile:
                            sms_message = SmsMessage(source="php", body=template_body, to=member.mobile)
                            sms_messages = clicksend_client.SmsMessageCollection(messages=[sms_message])
                            ast.literal_eval(smsapi_instance.sms_send_post(sms_messages))
                            contact = clicksend_client.Contact(
                                                phone_number= member.mobile or '',
                                                first_name= member.name or '',
                                                last_name="",
                                                custom_1= member.name,
                                                custom_2="",
                                                custom_3="",
                                                custom_4="",
                                                fax_number="",
                                                organization_name= member.company_id.name or '',
                                                email= member.email or '',
                                                address_line_1= member.street or '',
                                                address_line_2= member.street2 or '',
                                                address_city= member.city or '',
                                                address_state= member.state_id.name or '',
                                                address_postal_code= member.zip or '',
                                                address_country= member.country_id.code) # Contact | Contact model
                            list_id = list_id # int | List id
                            # Create new contact
                            ast.literal_eval(contact_api_instance.lists_contacts_by_list_id_post(contact, list_id))
                    order.state = 'sent'
                elif order.send_sms_type == 'multi_member':
                    api_instance = clicksend_client.SMSApi(clicksend_client.ApiClient(configuration))
                    for member in order.member_ids:
                        if not member.mobile:
                            raise UserError(_('Member Mobile Number Does Not Added'))
                        if member.mobile:
                            sms_message = SmsMessage(source="php", body=template_body, to=member.mobile)
                            sms_messages = clicksend_client.SmsMessageCollection(messages=[sms_message])
                            api_response = ast.literal_eval(api_instance.sms_send_post(sms_messages))
                            if api_response.get('response_code') == 'SUCCESS':
                                order.state = 'sent'
            elif order.account_id.account_gateway == 'textlocal':
                textlocal_authkey = order.account_id.textlocal_authkey
                textlocal_sender = order.account_id.textlocal_sender
                template_body = order.template_body
                if order.send_sms_type == 'individual_member':
                    sms_messages =  urllib.parse.urlencode({'apikey': textlocal_authkey, 'numbers': order.mobile_no,
                        'message' : template_body, 'sender': textlocal_sender})
                    sms_messages = sms_messages.encode('utf-8')
                    sms_request = urllib.request.Request("https://messagingsuite.smart.com.ph/cgphttp/servlet/sendmsg?destination=639190795972&text=GalingAkoSaOdoo")
                    api_responses = urllib.request.urlopen(sms_request, sms_messages)
                    api_response = ast.literal_eval(api_responses.read())
                    if api_response.get('status') == 'success':
                        order.state = 'sent'
                elif order.send_sms_type == 'group':
                    group_name = order.group_id.name
                    if not order.group_id.active:
                        message =  '"' + order.group_id.name + '"' + ' ' + "Was Deactive !. Please Active Groups"
                        raise UserError(_(message))
                    # Create Group
                    apikey = order.account_id.textlocal_authkey
                    sms_group_data =  urllib.parse.urlencode({'apikey': apikey, 'name' : group_name})
                    sms_group_data = sms_group_data.encode('utf-8')
                    sms_group_request = urllib.request.Request("https://api.textlocal.in/create_group/?")
                    api_responses = urllib.request.urlopen(sms_group_request, sms_group_data)
                    api_response = json.loads(api_responses.read())
                    if api_response.get('status') == 'success':
                        msg_group_id = api_response.get('group')
                        if msg_group_id:
                            order.group_id.mg_cont_group_id = msg_group_id.get('id')
                        # Added member In Group
                        group_id = msg_group_id.get('id')
                        member_ids = []
                        for member in order.group_id.member_ids:
                            if not member.mobile:
                                raise UserError(_('Member Mobile Number Does Not Added'))
                            if member.mobile:
                                contact_mobile_no = member.mobile
                                contact_first_name = member.name or ''
                                contact_last_name = ''
                                contact_custom1 = member.street or ''
                                contact_custom2 = member.street2 or ''
                                contact_custom3 = str(member.city or '') + ' ' + str(member.state_id.name or '') + ' ' + str(member.zip or '')
                                contact1 = {"number": contact_mobile_no,
                                            "first_name": contact_first_name,
                                            "last_name": contact_last_name,
                                            "custom1": contact_custom1,
                                            "custom2": contact_custom2,
                                            "custom3": contact_custom3,
                                            'groupID': group_id}
                                member_ids.append(contact1)
                        if member_ids:
                            contacts = json.JSONEncoder().encode(tuple(member_ids))
                            contacts_data =  urllib.parse.urlencode({'apikey': apikey, 'group_id' : group_id})
                            contacts_data = contacts_data + "&contacts=" + contacts
                            contacts_data = contacts_data.encode('utf-8')
                            contacts_request = urllib.request.Request("https://api.textlocal.in/create_contacts_bulk/?")
                            contacts_responses = urllib.request.urlopen(contacts_request, contacts_data)
                            contacts_response = json.loads(contacts_responses.read())
                            if contacts_response.get('status') == 'success':
                                for member in order.group_id.member_ids:
                                    sms_messages =  urllib.parse.urlencode({
                                        'apikey': apikey,
                                        'message' : template_body, 'sender': textlocal_sender,
                                        'group_id' : group_id
                                        })
                                    sms_messages = sms_messages.encode('utf-8')
                                    sms_request = urllib.request.Request("https://api.textlocal.in/send/?")
                                    api_responses = urllib.request.urlopen(sms_request, sms_messages)
                                    api_response = json.loads(api_responses.read())
                        order.state = 'sent'                                    
                    elif api_response.get('status') == 'failure':
                        message = api_response.get('errors')[0].get('message')
                        raise UserError(_(message))
                elif order.send_sms_type == 'multi_member':
                    for member in order.member_ids:
                        if not member.mobile:
                            raise UserError(_('Member Mobile Number Does Not Added'))
                        if member.mobile:
                            sms_messages =  urllib.parse.urlencode({
                                'apikey': textlocal_authkey, 'numbers': member.mobile,
                                'message' : template_body, 'sender': textlocal_sender,
                                })
                            sms_messages = sms_messages.encode('utf-8')
                            sms_request = urllib.request.Request("https://api.textlocal.in/send/?")
                            api_responses = urllib.request.urlopen(sms_request, sms_messages)
                            api_response = json.loads(api_responses.read())
                    order.state = 'sent'


    def action_delete_group(self):
        if self.account_id.account_gateway == 'msg91':
            conn = http.client.HTTPSConnection("control.msg91.com")
            access_token = self.account_id.msg_authkey
            msg_group_id = self.group_id.mg_cont_group_id
            conn.request("GET", "/api/delete_group.php?group_id=%s&authkey=%s" %\
                         (msg_group_id, access_token))
            member_result = conn.getresponse()
            member_data = member_result.read()
            member_dict = json.loads(member_data.decode("utf-8"))
            if member_dict.get('msgType') == 'success':
                message = '"' + self.group_id.name + '"' + ' ' + 'Was Deleted'
                self.group_id.mg_cont_group_id = ''
                raise UserError(_(message))
            else:
                message = 'This ' + '"' + self.group_id.name + '"' + ' ' + "doesn't Exist." 
                raise UserError(_(message))
        elif self.account_id.account_gateway == 'clicksend':
            configuration = clicksend_client.Configuration()
            configuration.username = self.account_id.clicksend_username
            configuration.password = self.account_id.clicksend_apikey
            # create an instance of the API class
            api_instance = clicksend_client.ContactListApi(clicksend_client.ApiClient(configuration))
            list_id = self.group_id.mg_cont_group_id # int | List ID.
            try:
                api_response = api_instance.lists_by_list_id_delete(list_id)
                print(api_response)
            except:
                raise UserError(_('Facing a Problems During Deleting Contact List'))
        elif self.account_id.account_gateway == 'textlocal':
            textlocal_authkey = self.account_id.textlocal_authkey
            groupID = self.group_id.mg_cont_group_id
            group_data =  urllib.parse.urlencode({'apikey': textlocal_authkey, 'group_id' : groupID})
            group_data = group_data.encode('utf-8')
            group_request = urllib.request.Request("https://api.textlocal.in/delete_group/?")
            group_responses = urllib.request.urlopen(group_request, group_data)
            group_response = json.loads(group_responses.read())
            if group_response.get('status') == 'success':
                message = '"' + self.group_id.name + '"' + ' ' + 'Was Deleted'
                self.group_id.mg_cont_group_id = ''
                raise UserError(_(message))
            else:
                message = 'This ' + '"' + self.group_id.name + '"' + ' ' + "doesn't Exist." 
                raise UserError(_(message))


    @api.onchange('template_id')
    def _get_template_id(self):
        for line in self:
            line.template_body = line.template_id.template_body
    

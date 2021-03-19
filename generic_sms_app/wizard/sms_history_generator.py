# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools, _
from datetime import datetime
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import ast
import time
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


class SmsHistoryGenerator(models.TransientModel):
	_name = "sms.history.generator"
	_description = 'SMS History Generator'

	start_date = fields.Date(string='Start Date', required=True,
							default=datetime.now().strftime('%Y-%m-01'))
	end_date = fields.Date(string='End Date', required=True,
		default=str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10])
	account_gateway = fields.Selection([('msg91','MSG91'),
										('clicksend','ClickSend'),
										('textlocal','TextLocal')], string="SMS Gateway")
	all_records = fields.Boolean('All Records', default=True)
	limit = fields.Integer('Limit', default=20)


	def generate_sms_history(self):
		for record in self:
			if record.account_gateway == 'clicksend':
				# Configure HTTP basic authorization: BasicAuth
				configuration_id = self.env['sms.account.configuration'].\
								search([('account_gateway','=', record.account_gateway)], limit=1)
				configuration = clicksend_client.Configuration()
				configuration.username = configuration_id.clicksend_username
				configuration.password = configuration_id.clicksend_apikey
				# create an instance of the API class
				api_instance = clicksend_client.SMSApi(clicksend_client.ApiClient(configuration))
				history_obj = self.env['sms.history']
				try:
					if record.all_records:
						# Get all sms history
						api_response = ast.literal_eval(api_instance.sms_history_get(limit= record.limit))
						api_response_data = api_response.get('data')
						api_response_datas = api_response_data.get('data')
						history_ids = history_obj.search([])
						if history_ids:
							history_ids.unlink()
						for records in api_response_datas:
							vals = {
								'contact_to': records.get('to'),
								'template_body': records.get('body'),
								'status': records.get('status'),
								'account_gateway': record.account_gateway,
							}
							history_obj.create(vals)
					else:
						# Get all sms history
						# Unixtime For Date From
						date_from = record.start_date
						date_from_unixtime = time.mktime(date_from.timetuple())
						# Unixtime For Date To
						date_to = record.end_date
						date_to_unixtime = time.mktime(date_to.timetuple())

						api_response = ast.literal_eval(api_instance.sms_history_get(date_from=date_from_unixtime, date_to=date_to_unixtime, limit= record.limit))
						api_response_data = api_response.get('data')
						api_response_datas = api_response_data.get('data')
						history_ids = history_obj.search([])
						if history_ids:
							history_ids.unlink()
						for records in api_response_datas:
							vals = {
								'contact_to': records.get('to'),
								'template_body': records.get('body'),
								'status': records.get('status'),
								'account_gateway': record.account_gateway,
							}
							history_obj.create(vals)
				except ApiException as e:
					UserError(_("Exception when calling SMSApi->sms_history_get: %s\n" % e))
			elif record.account_gateway == 'textlocal':
				configuration_id = self.env['sms.account.configuration'].\
								search([('account_gateway','=', record.account_gateway)], limit=1)
				textlocal_authkey = configuration_id.textlocal_authkey
				textlocal_sender = configuration_id.textlocal_sender
				history_obj = self.env['sms.history']
				try:
					if record.all_records:
						# Get all sms history
						api_data =  urllib.parse.urlencode({'apikey': textlocal_authkey, 'limit': record.limit})
						api_data = api_data.encode('utf-8')
						api_request = urllib.request.Request("https://api.textlocal.in/get_history_api/?")
						api_response = urllib.request.urlopen(api_request, api_data)
						api_response_datas = json.loads(api_response.read())
						history_ids = history_obj.search([])
						if api_response_datas.get('status') == 'success':
							if api_response_datas.get('messages') != []:
								if history_ids:
									history_ids.unlink()
								for records in api_response_datas.get('messages'):
									status = ''
									if records.get('status') == 'D':
										status = 'Delivered'
									else:
										status = 'Undelivered'
									vals = {
										'contact_to': records.get('number'),
										'template_body': records.get('content'),
										'status': status,
										'account_gateway': record.account_gateway,
									}
									history_obj.create(vals)
							else:
								UserError(_("No History Found !"))
						else:
							UserError(_("No History Found !"))
					else:
						# Get all sms history
						# Unixtime For Date From
						date_from = record.start_date
						date_from_unixtime = time.mktime(date_from.timetuple())
						# Unixtime For Date To
						date_to = record.end_date
						date_to_unixtime = time.mktime(date_to.timetuple())
						api_data =  urllib.parse.urlencode({'apikey': textlocal_authkey, 'limit': record.limit,
															'min_time': date_from_unixtime, 'max_time': date_to_unixtime})
						api_data = api_data.encode('utf-8')
						api_request = urllib.request.Request("https://api.textlocal.in/get_history_api/?")
						api_response = urllib.request.urlopen(api_request, api_data)
						api_response_datas = json.loads(api_response.read())
						history_ids = history_obj.search([])
						if api_response_datas.get('status') == 'success':
							if api_response_datas.get('messages') != []:
								if history_ids:
									history_ids.unlink()
								for records in api_response_datas.get('messages'):
									status = ''
									if records.get('status') == 'D':
										status = 'Delivered'
									else:
										status = 'Undelivered'
									vals = {
										'contact_to': records.get('number'),
										'template_body': records.get('content'),
										'status': status,
										'account_gateway': record.account_gateway,
									}
									history_obj.create(vals)
							else:
								UserError(_("No History Found !"))
						else:
							UserError(_("No History Found !"))
				except ValueError:
					pass




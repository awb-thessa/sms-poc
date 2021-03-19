# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):	
    _inherit = 'res.config.settings'	

    install_msg91_sms_gateway = fields.Boolean('MSG91 SMS Gateway')
    install_clicksend_sms_gateway = fields.Boolean('Clicksend SMS Gateway')
    install_textlocal_sms_gateway = fields.Boolean('TextLocal SMS Gateway')

    @api.model
    def default_get(self, fields):
        settings = super(ResConfigSettings, self).default_get(fields)
        settings.update(self.get_sms_account_config(fields))
        return settings

    @api.model
    def get_sms_account_config(self, fields):
        sms_account_config = \
                    self.env.ref('generic_sms_app.sms_account_config_data')
        return {
            'install_msg91_sms_gateway': sms_account_config.install_msg91_sms_gateway,
            'install_clicksend_sms_gateway': sms_account_config.install_clicksend_sms_gateway,
            'install_textlocal_sms_gateway': sms_account_config.install_textlocal_sms_gateway,
        }

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        sms_account_config = \
                    self.env.ref('generic_sms_app.sms_account_config_data')
        vals = {
            'install_msg91_sms_gateway': self.install_msg91_sms_gateway,
            'install_clicksend_sms_gateway': self.install_clicksend_sms_gateway,
            'install_textlocal_sms_gateway': self.install_textlocal_sms_gateway,
        }
        if self.install_msg91_sms_gateway:
            sms_account_config_id = self.env['sms.account.configuration'].search([('account_gateway','=', 'msg91')], limit=1)
            if sms_account_config_id:
                sms_account_config_id.write({'active': True})
        else:
            sms_account_config_id = self.env['sms.account.configuration'].search([('account_gateway','=', 'msg91')], limit=1)
            if sms_account_config_id:
                sms_account_config_id.write({'active': False})

        if self.install_clicksend_sms_gateway:
            sms_account_config_id = self.env['sms.account.configuration'].search([('account_gateway','=', 'clicksend')], limit=1)
            if sms_account_config_id:
                sms_account_config_id.write({'active': True})
        else:
            sms_account_config_id = self.env['sms.account.configuration'].search([('account_gateway','=', 'clicksend')], limit=1)
            if sms_account_config_id:
                sms_account_config_id.write({'active': False})

        if self.install_textlocal_sms_gateway:
            sms_account_config_id = self.env['sms.account.configuration'].search([('account_gateway','=', 'textlocal')], limit=1)
            if sms_account_config_id:
                sms_account_config_id.write({'active': True})
        else:
            sms_account_config_id = self.env['sms.account.configuration'].search([('account_gateway','=', 'textlocal')], limit=1)
            if sms_account_config_id:
                sms_account_config_id.write({'active': False})

        sms_account_config.write(vals)


class ResConfigSmsGatewayConfiguration(models.Model):
    _name = 'sms.account.config'
    _description = 'SMS Account Configuration'

    install_msg91_sms_gateway = fields.Boolean('Install MSG91 SMS Gateway')
    install_clicksend_sms_gateway = fields.Boolean('Install Clicksend SMS Gateway')
    install_textlocal_sms_gateway = fields.Boolean('Install TextLocal SMS Gateway')



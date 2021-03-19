# -*- coding: utf-8 -*-

{
    "name" : "Odoo SMS Gateway",
    "author": "Edge Technologies",
    "version" : "13.0.1.0",
    'live_test_url': "https://youtu.be/M6zej3XUwkA",
    "images":['static/description/main_screenshot.png'],
    "summary": 'Generic SMS Notification SMS gateway for odoo ClickSend sms Gateway Odoo MSG91 SMS gateway Odoo TextLocal SMS gateway ClickSend sms notification Odoo MSG91 SMS notification Odoo TextLocal SMS notification send sms from odoo odoo send sms odoo sms send',
    "description": """Generic SMS Notification""",
    "license" : "OPL-1",
    "depends" : ['base', 'sale_management', 'account', 'stock'],
    "data": [
        'security/ir.model.access.csv',
        'security/res_groups.xml',
        'data/sms_account_config_data.xml',
        'data/ir_sequence_data.xml',
        'data/sms_template_data.xml',
        'data/sms_gateway_config_data.xml',
        'views/res_config_settings_views.xml',
        'views/sms_account_views.xml',
        'views/sms_account_config_views.xml',
        'views/sms_template_view.xml',
        'views/sms_group_view.xml',
        'views/sms_history_view.xml',
        'wizard/sms_history_generator_views.xml',
     ],
    "installable": True,
    "auto_install": False,
    "price": 12,
    "currency": "EUR",
    "category": "Extra Tools",
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

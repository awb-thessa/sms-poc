# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import http
import json


class SmsGroup(models.Model):

    _name = "sms.groups"
    _description = "SMS Groups"

    def _member_count(self):
        partner_obj = self.env['res.partner']
        for group in self:
            group.member_count = partner_obj.search_count([('id', 'in', group.member_ids.ids)])

    name = fields.Char('Campaigns Name',default=lambda self: _('New'))
    member_type = fields.Selection([('customer','Customer'),('supplier','Supplier')], string="Contacts Type")
    member_ids = fields.Many2many('res.partner', 'sms_group_res_partner_rel', string='Contacts')
    member_count = fields.Integer(compute='_member_count', string='Total Contacts')
    mg_cont_group_id = fields.Char('Group/Contact List ID')
    active = fields.Boolean(default=True)



    @api.onchange('member_type')
    def _get_member_type(self):
        if self.member_type == 'customer':
            domain = [('customer_rank', '>', 0)]
            return {'domain': {'member_ids': domain}}
        else:
            domain = [('supplier_rank', '>', 0)]
            return {'domain': {'member_ids': domain}}


    def open_members_details(self):
        xml_id = 'base.view_partner_tree'
        tree_view_id = self.env.ref(xml_id).id
        xml_id = 'base.view_partner_form'
        form_view_id = self.env.ref(xml_id).id
        return {
            'name': _('Members'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'res_model': 'res.partner',
            'domain': [('id', 'in', self.member_ids.ids)],
            'type': 'ir.actions.act_window',
        }

class ResPartner(models.Model):

    _inherit = "res.partner"

    message = fields.Text("Message")


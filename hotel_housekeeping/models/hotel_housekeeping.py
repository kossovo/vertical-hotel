# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>)
#    Copyright (C) 2004 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
from openerp.exceptions import except_orm, Warning
from openerp import models,fields,api,_
from openerp import netsvc
import time


class product_category(models.Model):

    _inherit = "product.category"

    isactivitytype = fields.Boolean('Is Activity Type',default=lambda *a: True)

class hotel_housekeeping_activity_type(models.Model):

    _name = 'hotel.housekeeping.activity.type'
    _description = 'Activity Type'

    activity_id = fields.Many2one('product.category','Category',required=True, delegate=True, ondelete='cascade')

class hotel_activity(models.Model):

    _name = 'hotel.activity'
    _description = 'Housekeeping Activity'
    _inherits = {'product.product': 'h_id'}

    h_id = fields.Many2one('product.product','Product',required=True, delegate=True, ondelete='cascade')

class hotel_housekeeping(models.Model):

    _name = "hotel.housekeeping"
    _description = "Reservation"
    _inherit = ['mail.thread']

    # Here in v8 default value is written in field declaration so no more need
    # of _defaults dictionary..
    current_date = fields.Date(
        "Today's Date", required=True, default=lambda *a: time.strftime('%Y-%m-%d'),
        track_visibility='onchange')
    clean_type = fields.Selection(
        [('daily', 'Daily'), ('checkin', 'Check-In'), ('checkout', 'Check-Out')],
        'Clean Type', required=True, track_visibility='onchange')
    room_no = fields.Many2one('hotel.room', 'Room No', required=True, track_visibility='onchange')
    activity_lines =fields.One2many('hotel.housekeeping.activities','a_list','Activities',help='Details of housekeeping activities.')
    inspector = fields.Many2one(
        'res.users','Inspector' , required=True, track_visibility='onchange')
    inspect_date_time =fields.Datetime(
        'Inspect Date Time', required=True, track_visibility='onchange')
    quality = fields.Selection(
        [('bad', 'Bad'), ('good', 'Good'), ('ok', 'Ok')], 'Quality', required=True,
        track_visibility='onchange',
        help='Inspector inspect the room and mark as Bad, Good or Ok. ')
    state = fields.Selection(
        [
            ('dirty', 'Dirty'), ('clean', 'Clean'), ('inspect', 'Inspect'),
            ('done', 'Done'), ('cancel', 'Cancelled')
        ], 'State', select=True, required=True, readonly=True, default=lambda *a: 'dirty',
        track_visibility='onchange')

    @api.multi
    def action_set_to_dirty(self):
        self.write({'state': 'dirty'})
        wf_service = netsvc.LocalService('workflow')
        for id in self.ids:
            wf_service.trg_create(self._uid, self._name, self.id, self._cr)
        return True

    @api.multi
    def room_cancel(self):
        self.write({'state':'cancel'})
        return True

    @api.multi
    def room_done(self):
        self.write({'state':'done'})
        return True

    @api.multi
    def room_inspect(self):
        self.write({'state':'inspect'})
        return True

    @api.multi
    def room_clean(self):
        self.write({'state':'clean'})
        return True

class hotel_housekeeping_activities(models.Model):

    _name = "hotel.housekeeping.activities"
    _description = "Housekeeping Activities "

    a_list = fields.Many2one('hotel.housekeeping',string='Reservation')
    room_id = fields.Many2one('hotel.room',string='Room No')
    today_date = fields.Date('Today Date')
    activity_name = fields.Many2one('hotel.activity',string='Housekeeping Activity')
    housekeeper = fields.Many2one('res.users',string='Housekeeper' ,required=True)
    clean_start_time = fields.Datetime('Clean Start Time', required=True)
    clean_end_time = fields.Datetime('Clean End Time', required=True)
    dirty = fields.Boolean('Dirty', help='Checked if the housekeeping activity results as Dirty.')
    clean = fields.Boolean('Clean', help='Checked if the housekeeping activity results as Clean.')

    @api.constrains('clean_start_time','clean_end_time')
    def check_clean_start_time(self):
            if self.clean_start_time >= self.clean_end_time:
                raise except_orm(_('Warning'),_('Start Date Should be less than the End Date!'))

    @api.model
    def default_get(self,fields):
        """ To get default values for the object.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param fields: List of fields for which we want default values
        @param context: A standard dictionary
        @return: A dictionary which of fields with values.
        """
        if self._context is None:
            self._context = {}
        res = super(hotel_housekeeping_activities, self).default_get(fields)
        if self._context.get('room_id', False):
            res.update({'room_id':self._context['room_id']})
        if self._context.get('today_date', False):
            res.update({'today_date':self._context['today_date']})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

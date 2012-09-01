#!/usr/bin/python
#-*- coding: UTF-8 -*-

"""
 (c) 2012 - Copyright Pierre-Yves Chibon <pingou@pingoured.fr>

 Distributed under License GPLv3 or later
 You can find a copy of this license on the website
 http://www.gnu.org/licenses/gpl.html

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 MA 02110-1301, USA.
"""

import ConfigParser
import os

import flask

import fedocallib
from fedocallib.model import Calendar, Meeting, Reminder

CONFIG = ConfigParser.ConfigParser()
if os.path.exists('/etc/fedocal.cfg'):
    CONFIG.readfp(open('/etc/fedocal.cfg'))
else:
    CONFIG.readfp(open(os.path.join(os.path.dirname(
        os.path.abspath(__file__)),
        'fedocal.cfg')))

# Create the application.
APP = flask.Flask(__name__)
APP.secret_key = CONFIG.get('fedocal', 'secret_key')


@APP.route('/')
def index():
    session = fedocallib.create_session(CONFIG.get('fedocal', 'db_url'))
    calendars = Calendar.get_all(session)
    week = fedocallib.get_week(session, calendars[0])
    meetings = fedocallib.get_meetings(session, calendar)
    return flask.render_template('agenda.html',
        calendar=calendars[0],
        calendars=calendars,
        weekdays=weekdays,
        meetings=meetings)


@APP.route('/<calendar>')
def calendar(calendar):
    session = fedocallib.create_session(CONFIG.get('fedocal', 'db_url'))
    calendar = Calendar.by_id(session, calendar)
    calendars = Calendar.get_all(session)
    weekdays = fedocallib.get_week_days()
    meetings = fedocallib.get_meetings(session, calendar)
    return flask.render_template('agenda.html',
        calendar=calendar,
        calendars=calendars,
        weekdays=weekdays,
        meetings=meetings)


if __name__ == '__main__':
    APP.debug = True
    APP.run()

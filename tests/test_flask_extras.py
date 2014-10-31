#!/usr/bin/python
#-*- coding: utf-8 -*-

"""
 (c) 2014 - Copyright Pierre-Yves Chibon
 Author: Pierre-Yves Chibon <pingou@pingoured.fr>

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

 fedocal's flask application tests script
 - for special corner case to test
"""

__requires__ = ['SQLAlchemy >= 0.7', 'jinja2 >= 2.4']
import pkg_resources

import flask
import logging
import unittest
import sys
import os

from datetime import time
from datetime import timedelta

sys.path.insert(0, os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '..'))

import fedocal
import fedocal.fedocallib as fedocallib
import fedocal.fedocallib.model as model
from tests import (Modeltests, FakeUser, flask10_only, user_set, TODAY)


# pylint: disable=E1103
class ExtrasFlasktests(Modeltests):
    """ Extras Flask application tests. """

    def __setup_calendar(self):
        """ Set up basic calendar information. """
        obj = model.Calendar(
            calendar_name='test_calendar',
            calendar_contact='test@example.com',
            calendar_description='This is a test calendar',
            calendar_editor_group='fi-apprentice',
            calendar_admin_group='infrastructure-main2')
        obj.save(self.session)
        self.session.commit()
        self.assertNotEqual(obj, None)

    def setUp(self):
        """ Set up the environnment, ran before every tests. """
        super(ExtrasFlasktests, self).setUp()

        fedocal.APP.config['TESTING'] = True
        fedocal.APP.debug = True
        fedocal.APP.logger.handlers = []
        fedocal.APP.logger.setLevel(logging.CRITICAL)
        fedocal.SESSION = self.session
        self.app = fedocal.APP.test_client()

    @flask10_only
    def test_start_date_edit_meeting_form(self):
        """ Test the content of the start_date in the edit meeting form.
        """
        self.__setup_calendar()

        calendar = model.Calendar.by_id(self.session, 'test_calendar')
        # Create a meeting
        obj = model.Meeting(  # id:1
            meeting_name='recursive meeting',
            meeting_date=TODAY,
            meeting_date_end=TODAY,
            meeting_time_start=time(19, 50),
            meeting_time_stop=time(20, 50),
            meeting_information='This is a test meeting',
            calendar_name='test_calendar',
            recursion_frequency=14,
            recursion_ends=TODAY + timedelta(days=90))
        obj.add_manager(self.session, 'pingou,')
        obj.save(self.session)
        self.session.commit()
        self.assertNotEqual(obj, None)

        user = FakeUser(['fi-apprentice'], username='pingou')
        with user_set(fedocal.APP, user):
            output = self.app.get('/meeting/edit/1/')
            self.assertEqual(output.status_code, 200)

            # If no date is specified, it returns the next occurence
            self.assertTrue(
                '<input id="meeting_date" name="meeting_date" type="text" '
                'value="%s">' % (TODAY + timedelta(days=14))
                in output.data
            )

            # If a date in the future is specified, return the next occurence
            # for this date
            url = '/meeting/edit/1/?from_date=%s' % (
                TODAY + timedelta(days=20))
            output2 = self.app.get(url)
            self.assertEqual(output2.status_code, 200)

            self.assertTrue(
                '<input id="meeting_date" name="meeting_date" type="text" '
                'value="%s">' % (TODAY + timedelta(days=28))
                in output2.data
            )

            # If an exact date in the future is specified, return that date
            url = '/meeting/edit/1/?from_date=%s' % (
                TODAY + timedelta(days=14))
            output2 = self.app.get(url)
            self.assertEqual(output2.status_code, 200)

            self.assertTrue(
                '<input id="meeting_date" name="meeting_date" type="text" '
                'value="%s">' % (TODAY + timedelta(days=14))
                in output2.data
            )

            # If an old date in the future is specified, return the first date
            output2 = self.app.get('/meeting/edit/1/?from_date=2000-01-01')
            self.assertEqual(output2.status_code, 200)

            self.assertTrue(
                '<input id="meeting_date" name="meeting_date" type="text" '
                'value="%s">' % (TODAY)
                in output2.data
            )

    @flask10_only
    def test_start_date_delete_meeting_form(self):
        """ Test the content of the start_date in the delete meeting form.
        """
        self.__setup_calendar()

        calendar = model.Calendar.by_id(self.session, 'test_calendar')
        # Create a meeting
        obj = model.Meeting(  # id:1
            meeting_name='recursive meeting',
            meeting_date=TODAY,
            meeting_date_end=TODAY,
            meeting_time_start=time(19, 50),
            meeting_time_stop=time(20, 50),
            meeting_information='This is a test meeting',
            calendar_name='test_calendar',
            recursion_frequency=14,
            recursion_ends=TODAY + timedelta(days=90))
        obj.add_manager(self.session, 'pingou,')
        obj.save(self.session)
        self.session.commit()
        self.assertNotEqual(obj, None)

        user = FakeUser(['fi-apprentice'], username='pingou')
        with user_set(fedocal.APP, user):
            output = self.app.get('/meeting/delete/1/')
            self.assertEqual(output.status_code, 200)

            # If no date is specified, it returns the next occurence
            self.assertTrue(
                '<li>Date: %s</li>' % (TODAY + timedelta(days=14))
                in output.data
            )

            # If a date in the future is specified, return the next occurence
            # for this date
            url = '/meeting/delete/1/?from_date=%s' % (
                TODAY + timedelta(days=20))
            output2 = self.app.get(url)
            self.assertEqual(output2.status_code, 200)

            self.assertTrue(
                '<li>Date: %s</li>' % (TODAY + timedelta(days=28))
                in output2.data
            )

            # If an exact date in the future is specified, return that date
            url = '/meeting/delete/1/?from_date=%s' % (
                TODAY + timedelta(days=14))
            output2 = self.app.get(url)
            self.assertEqual(output2.status_code, 200)

            self.assertTrue(
                '<li>Date: %s</li>' % (TODAY + timedelta(days=14))
                in output2.data
            )

            # If an old date in the future is specified, return the first date
            output2 = self.app.get('/meeting/delete/1/?from_date=2000-01-01')
            self.assertEqual(output2.status_code, 200)

            self.assertTrue(
                '<li>Date: %s</li>' % (TODAY) in output2.data
            )

if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(ExtrasFlasktests)
    unittest.TextTestRunner(verbosity=2).run(SUITE)

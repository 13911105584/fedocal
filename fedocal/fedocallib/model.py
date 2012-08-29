# -*- coding: utf-8 -*-

"""
model - an object mapper to a SQL database representation of the data
        stored in this project.

Copyright (C) 2012 Pierre-Yves Chibon
Author: Pierre-Yves Chibon <pingou@pingoured.fr>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or (at
your option) any later version.
See http://www.gnu.org/copyleft/gpl.html  for the full text of the
license.
"""
__requires__ = ['SQLAlchemy >= 0.7']
import pkg_resources

from datetime import datetime

from sqlalchemy import (
    create_engine,
    Column,
    Date,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relation as relationship
from sqlalchemy.orm.exc import NoResultFound

BASE = declarative_base()


def create_tables(db_url, debug=False):
    """ Create the tables in the database using the information from the
    url obtained.

    :arg db_url, URL used to connect to the database. The URL contains
    information with regards to the database engine, the host to connect
    to, the user and password and the database name.
      ie: <engine>://<user>:<password>@<host>/<dbname>
    :arg debug, a boolean specifying wether we should have the verbose
    output of sqlalchemy or not.
    :return a session that can be used to query the database.
    """
    engine = create_engine(db_url, echo=debug)
    BASE.metadata.create_all(engine)
    sessionmak = sessionmaker(bind=engine)
    return sessionmak()


def create_session(db_url, debug=False, pool_recycle=3600):
    """ Create the Session object to use to query the database.

    :arg db_url, URL used to connect to the database. The URL contains
    information with regards to the database engine, the host to connect
    to, the user and password and the database name.
      ie: <engine>://<user>:<password>@<host>/<dbname>
    :arg debug, a boolean specifying wether we should have the verbose
    output of sqlalchemy or not.
    :return a Session that can be used to query the database.
    """
    engine = create_engine(db_url, echo=debug, pool_recycle=pool_recycle)
    session = sessionmaker(bind=engine)
    return session()


class Calendar(BASE):
    """ Calendara table.

    Define the calendar available in this application.
    """

    __tablename__ = 'calendars'
    calendar_name = Column(String(80), primary_key=True)
    calendar_description = Column(String(500))
    calendar_manager_group = Column(String(100))  # 3 groups (3*32)

    def __init__(self, calendar_name, calendar_description,
        calendar_manager_group):
        """ Constructor instanciating the defaults values. """
        self.calendar_name = calendar_name
        self.calendar_description = calendar_description
        self.calendar_manager_group = calendar_manager_group

    def __repr__(self):
        """ Representation of the Calendar object when printed.
        """
        return "<Calendar('%s')>" % (self.calendar_name)

    def save(self, session):
        """ Save the object into the database. """
        session.add(self)

    @classmethod
    def by_id(cls, session, identifier):
        """ Retrieve a Calendar object from the database based on its
        identifier.
        :return None if no calendar matched this identifier.
        """
        try:
            return session.query(cls).get(identifier)
        except NoResultFound:
            return None


class Reminder(BASE):
    """ Reminders table.

    Store the information about the reminders that should be sent
    when asked in a meeting.
    """

    __tablename__ = 'reminders'
    reminder_id = Column(Integer, primary_key=True)
    reminder_offset = Column(Enum('H-12', 'H-24', 'H-48', 'H-168'))
    reminder_to = Column(String(500))
    reminder_text = Column(Text)

    def __init__(self, reminder_offset, reminder_to, reminder_text):
        """ Constructor instanciating the defaults values. """
        self.reminder_offset = reminder_offset
        self.reminder_to = reminder_to
        self.reminder_text = reminder_text

    def __repr__(self):
        """ Representation of the Reminder object when printed.
        """
        return "<Reminder('%s', '%s')>" % (self.reminder_to,
            self.reminder_offset)

    def save(self, session):
        """ Save the object into the database. """
        session.add(self)

    @classmethod
    def by_id(cls, session, identifier):
        """ Retrieve a Calendar object from the database based on its
        identifier.
        :return None if no calendar matched this identifier.
        """
        try:
            return session.query(cls).get(identifier)
        except NoResultFound:
            return None

class Meeting(BASE):
    """ Meetings table.

    Store the information about the meetings set in the application.
    """

    __tablename__ = 'meetings'
    meeting_id = Column(Integer, primary_key=True)
    meeting_name = Column(String(200))
    calendar_name = Column(String(80), ForeignKey('calendars.calendar_name'))
    calendar = relationship("Calendar")
    meeting_manager = Column(String(160))  #  5 person max (32 * 5)
    meeting_start = Column(Date, default=datetime.utcnow().date())
    meeting_stop = Column(Date, default=datetime.utcnow().date())
    meeting_time = Column(Date, default=datetime.utcnow().time())
    reminder_id = Column(Integer, ForeignKey('reminders.reminder_id'))
    reminder = relationship("Reminder")

    def __init__(self, meeting_name, meeting_manager,
        meeting_start, meeting_stop, meeting_time,
        calendar_name, reminder_id):
        """ Constructor instanciating the defaults values. """
        self.meeting_name = meeting_name
        self.meeting_manager = meeting_manager
        self.meeting_start = meeting_start
        self.meeting_stop = meeting_stop
        self.meeting_time = meeting_time
        self.calendar_name = calendar_name
        self.reminder_id = reminder_id

    def __repr__(self):
        """ Representation of the Reminder object when printed.
        """
        return "<Meeting('%s', '%s')>" % (self.calendar,
            self.meeting_name)

    def save(self, session):
        """ Save the object into the database. """
        session.add(self)

    @classmethod
    def by_id(cls, session, identifier):
        """ Retrieve a Calendar object from the database based on its
        identifier.
        :return None if no calendar matched this identifier.
        """
        try:
            return session.query(cls).get(identifier)
        except NoResultFound:
            return None

if __name__ == '__main__':
    create_tables('sqlite:///:memory:', True)

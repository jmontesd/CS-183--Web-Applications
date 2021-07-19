"""
This file defines the database models
"""
import datetime

from .common import db, Field, auth
from pydal.validators import *


### Define your table below
def get_user_email():
    return auth.current_user.get('email')


db.define_table('person',
                Field('user_email', default=get_user_email),
                Field('first_name', requires=IS_NOT_EMPTY()),
                Field('last_name', requires=IS_NOT_EMPTY()))

db.define_table('phone',
                Field('phone'),
                Field('kind'),
                Field('person_id', 'reference person', required=True))

db.person.id.readable = False
db.person.user_email.readable = False

db.commit()



"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *
import uuid


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None


def get_time():
    return datetime.datetime.utcnow()


# To keep track of all the devices:
db.define_table('device',
                # Field('device_id', 'string', writable=False, required=True, default=uuid.uuid4()),
                Field('device_name', 'string', required=True),
                Field('device_mac_address', 'string', required=True),
                Field('device_nickname', 'string'),
                Field('description', 'text'),
                Field('device_added_date', 'datetime', writable=False, default=get_time()),
                Field('user_email', 'string', writable=False, required=True, default=get_user_email)
                )

# db.device.id.readable = False
db.device.device_added_date.readable = False
db.device.user_email.readable = False

# db.device.device_name.widget = lambda f, v: SQLFORM.widgets.string.widget(f, v, _placeholder='Enter the name of device')
# db.device.description.widget = lambda f, v: SQLFORM.widgets.string.widget(f, v, _placeholder='Enter a description here')


# with this new split table definition it makes sense to just use the automatic id in this table as the procedure_id
# Name of procedure used for file on client should be unique per device_id
db.define_table('procedures_map',
                Field('device_id', 'string', required=True),
                Field('procedure_name', 'string', required=True)
                )


db.define_table('procedure_revisions',
                Field('procedure_id', 'bigint', required=True),  # key
                Field('procedure_code', 'text', required=True),
                # Actual code for procedure - is check IS_LENGTH(65536) ok?
                # Otherwise use string and specifiy larger length
                Field('last_update', 'datetime', default=get_time(), required=True),
                Field('is_stable', 'boolean', required=True)  # True for stable False for not stable
                )

db.define_table('procedure',
                Field('device_id', 'reference device', required=True),
                Field('procedure_id', 'string'),  # key
                Field('procedure_name', 'string'),
                Field('procedure_code', 'text', required=True),
                Field('last_updated', 'datetime', default=get_time(), required=True),
                # Field('is_deployed', 'boolean', required=True) //TODO
                )

##############
# Permission table.

# Permission types.
# v = view
# a = admin (valid only for one whole device)
# e = edit settings of procedure
db.define_table('user_permission',
                Field('perm_user_email', required=True),
                # The email of the currently logged in user can be found in auth.user.email
                Field('device_id', required=True),
                Field('procedure_id'),  # If this is Null, then permission is for whole device.
                # If None, then the permission is valid for ALL procedures.
                Field('perm_type', required=True)  # 'e'=edit, 'v'=view, etc.
                # See above.
                )

#########################
# Settings are synched "down" to the client.

db.define_table('client_setting',
                Field('device_id'),
                Field('procedure_id'),  # Can be Null for device-wide settings.
                Field('setting_name'),
                Field('setting_value'),  # Encoded in json-plus.
                Field('last_updated', 'datetime')
                )

##################################################
# These tables are synched "up" from the clients to the server.

# Synched client -> server
db.define_table('device_logs',
                Field('device_id'),
                Field('procedure_id'),  ## MOVE TO procedure_id
                Field('log_level', 'integer'),  # int, 0 = most important.
                Field('log_message', 'text'),
                Field('time_stamp', 'datetime'),
                Field('received_time_stamp', 'datetime', default=datetime.datetime.utcnow())
                )

# Synched client -> server
db.define_table('device_outputs',
                Field('device_id'),
                Field('procedure_id'),
                Field('field_name'),  # Name of variable
                Field('description'),
                Field('output_value', 'text'),  # Json, short please
                Field('comments'),
                Field('tag'),
                Field('time_stamp', 'datetime'),
                Field('received_time_stamp', 'datetime', default=datetime.datetime.utcnow()),
                )

# always commit your models to avoid problems later
db.commit()

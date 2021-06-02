"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

import time

from py4web import action, request, abort, redirect, URL
from py4web.utils.form import Form, FormStyleBulma

from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email

# from py4web.utils.publisher import Publisher, ALLOW_ALL_POLICY

from pydal.restapi import RestAPI, Policy

# publisher = Publisher(db, policy=ALLOW_ALL_POLICY)

url_signer = URLSigner(session)
currently_viewing_device_id = None


@action('index')
@action.uses(db, auth, 'index.html')
def index():
    print("in index():", get_user_email())
    return dict()

# ------------------------------------
# This page is accessible only to logged-in users.


@action('add_device', method=['GET', 'POST'])
@action.uses(session, db, auth.user, 'register_device.html')
def add_product():
    form = Form(db.device, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # We always want POST requests to be redirected as GETs.
        redirect(URL('add_device'))
    return dict(form=form)


@action('view_devices', method='GET')
@action.uses(session, db, auth.user, 'view_devices.html')
def view_products():
    # fetch all table rows
    rows = db(db.device).select()
    return dict(rows_devices=rows)


@action('edit_device/<device_id>', method=['GET', 'POST'])
@action.uses(session, db, auth.user, 'register_device.html')
def edit_product(device_id=None):
    """Note that in the above declaration, the product_id argument must match
    the <product_id> argument of the @action."""
    # We read the product.
    p = db.device[device_id]
    if p is None:
        # Nothing to edit.  This should happen only if you tamper manually with the URL.
        redirect(URL('view_devices'))
    form = Form(db.device, record=p, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # We always want POST requests to be redirected as GETs.
        redirect(URL('view_devices'))
    return dict(form=form)


@action('device/<device_id>', method=['GET', 'POST'])
@action.uses(session, db, auth.user, 'device.html')
def view_device(device_id=None):
    global currently_viewing_device_id
    currently_viewing_device_id = device_id

    p = db.device[currently_viewing_device_id]
    if p is None:
        # invalid device id
        redirect(URL('view_devices'))

    print("device id:", currently_viewing_device_id)
    # form = Form(db.device, record=p, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
    # if form.accepted:
    # We always want POST requests to be redirected as GETs.
    # redirect(URL('device'))
    # return dict()
    return dict(
        # This is the signed URL for the callback.
        # add_proc_url=URL('add_proc', signer=url_signer),
        # load_procs_url=URL('load_procedures', signer=url_signer),
        # edit_proc_url=URL('edit_procedure', signer=url_signer),
        # delete_proc_url=URL('delete_procedure', signer=url_signer),
        load_procedure_url=URL('load_procedure', signer=url_signer),
        load_logs_url=URL('load_logs', signer=url_signer),
        load_outputs_url=URL('load_outputs', signer=url_signer)

    )


@action('load_procedure')
@action.uses(url_signer.verify(), db)
def load_procedure():
    rows = db(db.procedure).select().as_list()
    return dict()
# db.define_table('procedure',
#                 Field('device_id', 'reference device', required=True),
#                 Field('procedure_id', 'string', required=True),  # key
#                 Field('procedure_name', 'string'),
#                 Field('procedure_code', 'text', required=True),
#                 Field('last_updated', 'datetime', default=get_time(), required=True),
#                 Field('is_deployed', 'boolean', required=True)
#                 )


@action('load_outputs')
@action.uses(url_signer.verify(), db)
def load_outputs():
    rows = db(db.device_outputs.device_id == currently_viewing_device_id ).select(orderby=~db.device_outputs.received_time_stamp).as_list()
    print("printed from slugIOT server - loaded output table: ", rows)
    return dict(rows=rows)


@action('load_logs')
@action.uses(url_signer.verify(), db)
def load_logs():
    print("currently_viewing_device_id", currently_viewing_device_id)
    rows = db(db.device_logs.device_id == currently_viewing_device_id).select(orderby=~db.device_logs.received_time_stamp).as_list()
    print("printed from slugIOT server - loaded logs table: ", rows)
    return dict(rows=rows)


# @action('edit_code', method='GET')
# @action.uses(session, db, auth.user, 'code_editor.html')
# def edit_code():
#     print("User::::", get_user_email())
#     return dict()





# @action('add_proc', method="POST")
# @action.uses(url_signer.verify(), db)
# def add_procedure():
#     id = db.procedures_map.insert(
#         device_id=request.json.get('device_id'),
#         procedure_name=request.json.get('procedure_name'),
#     )
#     return dict(id=id)


# @action('delete_procedure')
# @action.uses(url_signer.verify(), db)
# def delete_procedure():
#     id = request.params.get('id')
#     assert id is not None
#     db(db.procedures_map.id == id).delete()
#     return "ok"


# @action('edit_procedure', method="POST")
# @action.uses(url_signer.verify(), db)
# def edit_procedure():
#     id = request.json.get("id")
#     field = request.json.get("field")
#     value = request.json.get("value")
#     db(db.procedures_map.id == id).update(**{field: value})
#     time.sleep(1)  # debugging
#     return "ok"


##############################################################################
# RestAPI Call Handling
# The SlugIOT Client sends POST requests to update device outputs and logs.
##############################################################################

rest_policy = Policy()
rest_policy.set('device', 'GET', authorize=True, allowed_patterns=['*'])
rest_policy.set('procedure', 'GET', authorize=True, allowed_patterns=['*'])
rest_policy.set('device_logs', 'POST', authorize=True)
rest_policy.set('device_outputs', 'POST', authorize=True)

# For security reasons we disabled all the other methods at the policy level
# To enable any of them just set authorize = True
rest_policy.set('*', 'PUT', authorize=False)
rest_policy.set('*', 'DELETE', authorize=False)


# http://127.0.0.1:8000/SlugIOT_Server/api/device/<device_id>
# http://127.0.0.1:8000/SlugIOT_Server/api/procedure/<device_id>
# http://127.0.0.1:8000/SlugIOT_Server/api/device_logs/<device_id>
# http://127.0.0.1:8000/SlugIOT_Server/api/device_outputs/<device_id>
@action('api/<tablename>/', method=['GET', 'POST'])
@action('api/<tablename>/<rec_id>', method=['GET', 'PUT', 'DELETE'])
@action.uses(db)
def api(tablename, rec_id=None):
    print(request);
    return RestAPI(db, rest_policy)(request.method,
                                    tablename,
                                    rec_id,
                                    request.GET,
                                    # request.POST
                                    request.json
                                    )

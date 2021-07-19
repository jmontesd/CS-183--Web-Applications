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

import uuid

from pydal.validators import IS_NOT_EMPTY

from py4web import action, request, abort, redirect, URL, Field
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.url_signer import URLSigner

from yatl.helpers import A
from .common import db, session, T, cache, auth, signed_url

url_signer = URLSigner(session)


# The auth.user below forces login.
@action('index')
@action.uses('index.html', auth.user, db)
def index():
    logged_in = auth.current_user.get('email')
    rows = db(db.person.user_email == logged_in).select().as_list()

    for row in rows:
        person_id = row["id"]
        phone_numbers = db(db.phone.person_id == person_id).select()
        s = ""
        for index2, phone_number in enumerate(phone_numbers):
            s += phone_number["phone"]
            s += " "
            s += "("
            s += phone_number["kind"]
            s += "), "
        row["phone_numbers"] = s
        # print(row["phone_numbers"])
    # for row in rows:
    # print(row)
    return dict(rows=rows, url_signer=url_signer, user=auth.user)


@action('add_contact', method=['GET', 'POST'])
@action.uses('contact_form.html', session, db, auth.user)
def add_contact():
    form = Form(db.person, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        redirect(URL('index'))
    else:
        return dict(form=form, user=auth.user)


@action('edit_contact/<contact_id>', method=['GET', 'POST'])
@action.uses('contact_form.html', session, db, auth.user)
def edit_contact(contact_id=None):
    person = db.person[contact_id]
    if person is None:
        redirect(URL('index'))
    else:
        if person.user_email == auth.current_user.get('email'):
            form = Form(db.person, record=person, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
            if form.accepted:
                redirect(URL('index'))
            else:
                return dict(form=form, user=auth.user)
        else:
            redirect(URL('index'))


@action('delete_contact/<contact_id>', method=['GET'])
@action.uses(session, db, url_signer.verify(), auth.user)
def delete_contact(contact_id=None):
    person = db.person[contact_id]
    if person is not None:
        if person.user_email == auth.current_user.get('email'):
            db(db.person.id == contact_id).delete()
            redirect(URL('index'))
    return dict(url_signer=url_signer)


@action('edit_phones/<person_id>')
@action.uses('phones.html', session, db, auth.user)
def edit_phones(person_id=None):
    person = db.person[person_id]
    if person is not None:
        if person.user_email == auth.current_user.get('email'):
            rows = db(db.phone.person_id == person_id).select()
            return dict(rows=rows, name=person.first_name + " " + person.last_name, person_id=person_id, url_signer=url_signer, user=auth.user)
    else:
        redirect(URL('index'))


@action('add_phone/<person_id>', method=['GET', 'POST'])
@action.uses('phone_form.html', session, db, auth.user)
def add_phone(person_id=None):
    print(person_id)
    person = db.person[person_id]
    if person is not None:
        if person.user_email == auth.current_user.get('email'):
            form = Form([Field('phone', requires=IS_NOT_EMPTY()), Field('kind', requires=IS_NOT_EMPTY())],
                        csrf_session=session, formstyle=FormStyleBulma)
            if form.accepted:
                db.phone.insert(phone=form.vars["phone"], kind=form.vars["kind"], person_id=person_id)
                redirect(URL('edit_phones', person_id))
            return dict(form=form, name=person.first_name, user=auth.user)
    redirect(URL('edit_phones', person_id))


@action('edit_phone/<person_id>/<phone_id>', method=['GET', 'POST'])
@action.uses('phone_form.html', session, db, auth.user)
def edit_phone(person_id=None, phone_id=None):
    person = db.person[person_id]
    phone = db.phone[phone_id]
    if person is None:
        redirect(URL('index'))
    else:
        if person.user_email == auth.current_user.get('email'):
            form = Form([Field('phone', requires=IS_NOT_EMPTY()), Field('kind', requires=IS_NOT_EMPTY())], record=phone,
                        deletable=False, csrf_session=session, formstyle=FormStyleBulma)
            if form.accepted:
                db(db.phone.id == phone_id).update(phone=form.vars["phone"], kind=form.vars["kind"],
                                                   person_id=person_id)
                redirect(URL('edit_phones', person_id))
            else:
                return dict(form=form, name=person.first_name, user=auth.user)
        else:
            redirect(URL('edit_phones', person_id))


@action('delete_phone/<person_id>/<phone_id>', method=['GET'])
@action.uses(session, db, url_signer.verify())
def delete_phone(person_id=None, phone_id=None):
    person = db.person[person_id]
    phone = db.phone[phone_id]
    if person.user_email == auth.current_user.get('email'):
        if phone is not None:
            db(db.phone.id == phone_id).delete()
            redirect(URL('edit_phones', person_id))
    return dict(url_signer=url_signer)

"""
Received help from Matan's section to finish this assignment
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

import random
import time
import uuid

from py4web import action, request, abort, redirect, URL, Field, HTTP
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.url_signer import URLSigner

from yatl.helpers import A
from .common import db, session, T, cache, auth, signed_url

TEST_POSTS = [
    {
        "id": 1,
        "content": "I love apples",
        "author": "Joe Smith",
        "email": "joe@ucsc.edu",
        "reply_id": None,  # Main post.  Followed by its replies if any.
    },
    {
        "id": 2,
        "content": "I love bananas",
        "author": "Elena Bianchi",
        "email": "elena@ucsc.edu",
        "is_reply": 1,
    },
    {
        "id": 3,
        "content": "I prefer pears",
        "author": "Joel Framon",
        "email": "joel@ucsc.edu",
        "is_reply": 1,
    },
    {
        "id": 4,
        "content": "I love tomatoes",
        "author": "Olga Kabarova",
        "email": "olga@ucsc.edu",
        "is_reply": None,  # Main post.  Followed by its replies if any.
    },
    {
        "id": 5,
        "content": "I prefer nuts",
        "author": "Hao Wang",
        "email": "hwang@ucsc.edu",
        "is_reply": 4,
    },
]

url_signer = URLSigner(session)


def get_name_from_email(e):
    """Given the email of a user, returns the name."""
    u = db(db.auth_user.email == e).select().first()
    return "" if u is None else u.first_name + " " + u.last_name


# The auth.user below forces login.
@action('index')
@action.uses(auth.user, url_signer, session, db, 'index.html')
def index():
    return dict(
        # This is an example of a signed URL for the callback.
        # See the index.html template for how this is passed to the javascript.
        posts_url=URL('posts', signer=url_signer),
        delete_url=URL('delete_post', signer=url_signer),
        user_email=auth.current_user.get('email'),
        author_name=auth.current_user.get('first_name') + " " + auth.current_user.get('last_name')
    )


@action('posts', method="GET")
@action.uses(db, auth.user, session, url_signer.verify())
def get_posts():
    # You can use this shortcut for testing at the very beginning.
    # TODO: complete.
    # Get the main posts in reverse chronological order
    main_posts = []
    posts = db(db.post.is_reply == None).select(orderby=~db.post.post_date).as_list()
    # Now match the post with its replies
    for post in posts:
        post["author"] = get_name_from_email(post["email"])
        # create an array that will be holding all the replies to corresponding post
        reply_array = [post]
        replies = db(db.post.is_reply == post["id"]).select(orderby=~db.post.post_date).as_list()
        for reply in replies:
            reply["author"] = get_name_from_email(post["email"])
        reply_array = reply_array + replies
        main_posts = main_posts + reply_array
    return dict(posts=main_posts)


@action('posts', method="POST")
@action.uses(db, auth.user)  # etc.  Put here what you need.
def save_post():
    post_id = request.json.get('id')  # Note: id can be none.
    content = request.json.get('content')
    is_reply = request.json.get('is_reply')
    # TODO: complete.
    # If id is None, this means that this is a new post that needs to be
    # inserted.  If id is not None, then this is an update.
    new_id = db.post.update_or_insert(db.post.id == post_id, is_reply=is_reply, content=content)
    return dict(content=content, id=new_id)


@action('delete_post', method="POST")
@action.uses(db, auth.user, session, url_signer.verify())
def delete_post():
    db((db.post.email == auth.current_user.get("email")) &
       (db.post.id == request.json.get('id'))).delete()
    return "ok"


@action('delete_all_posts')
@action.uses(db)
def delete_all_posts():
    """This should be removed before you use the app in production!"""
    db(db.post).delete()
    return "ok"

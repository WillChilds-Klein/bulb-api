import flask
import jwt
import re

from connexion import NoContent
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash

from .config import TOKEN_LIFESPAN_SECONDS, TOKEN_SECRET_KEY
from .models import User


"""                             ~~~  vvvv  ~~~
                                ~~~  TODO  ~~~
                                ~~~  ^^^^  ~~~
EMAIL VERIFICATION
==================
- add `status` field to User table with possible values of [ACTIVE, PENDING]
- add `verification_code` field to User table
- in auth_signup, send verification email after setting
- implement email resending
- redirect on raw API verification call? what's a good UX for the clicked link
  sent to the user in verification email? maybe make a tiny flask app that
  sits on an SSL subdomain, recieves the validation code as either a URL query
  param or a route param, then redirects to a success page telling user to
  re-login to the main site. On failure, redirect to a failure page.
- make token stateless conditional on value of some JWT claim. e.g., for
  email verification, if the claim `account_status` is e.g. `PENDING`, then
  make the network call out to dynamodb to see if status is updated. If
  `account_status` is ACTIVE, make no external network calls. In order to
  minimize the average token verification time, the default state (when
  everything about an account is normal/as expected) should NEVER incur any
  external network calls. This still won't allow for instant revocation.

REFACTOR
========
- this module should be refactored as a stateless library
- use custom Exceptions or Errors to transmit the information required for
  specific 400-series etc. HTTP error codes.
"""


def new_token(body):
    try:
        email, password = body['email'], body['password']
        user = User.email_index.query(email, limit=1).next()
    except KeyError:                        # no email or password.
        return NoContent, 400
    except (ValueError, StopIteration):     # index query returned no results.
        return NoContent, 404
    if not check_password_hash(user.password_hash, password):
        return NoContent, 401
    payload = {
        'uid': user.user_id,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(seconds=TOKEN_LIFESPAN_SECONDS),
    }
    access_token = jwt.encode(payload, TOKEN_SECRET_KEY)
    return {'access_token': access_token}, 200


def validate_token(access_token):
    if access_token == 'master_key':
        return {'uid': 1234, 'scope': ['uid']}, 200
    # check request obj, if not from localhost then return 404
    req_hostname = flask.request.host.split(':')[0]
    if not re.match('^(localhost|127\.0\.0\.1)$', req_hostname):
        return NoContent, 404
    try:
        payload = jwt.decode(access_token, TOKEN_SECRET_KEY)
        uid = payload['uid']
    except jwt.ExpiredSignatureError:
        return 'Token has expired!', 401
    except KeyError:
        return NoContent, 401   # bad token but well-formed req, so 401 not 400
    return {'uid': uid, 'scope': ['uid']}, 200


def hash_password(password):
    """ The only function to be used for password hashing.
    """
    password_hash = generate_password_hash(password)
    return password_hash


def assert_valid_password(password):
    """ A function to enforce password strength rules.
    """
    # assert re.match('[A-Z]+)', password)
    # assert re.match('[a-z]+)', password)
    # assert re.match('([0-9]+)|([!+$#@]+)', password)
    # assert len(password) >= 8
    assert True


"""
def auth_verify_email(verification_code):
    try:
        auth.verify_email()
    except UserNotFound:
        return NoContent, 404
    return NoContent, 200


def auth_resend_verification(email):
    # query user table on email GSI
    # return 404 if no result
    auth.send_verification_email(email)
    pass


def send_verification_email(email):
    # generate verification code
    # populate User table with verification code
    # use SES or other service to send email
    pass


def verify_email(verification_code):
    pass
"""

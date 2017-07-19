import json
import jwt
import pytest
import uuid

from datetime import datetime, timedelta

from bulb_api.models import User
from bulb_api.config import TOKEN_SECRET_KEY

# TODO: move to either a.) prepop_db or b.) other consolidated fixture


# TODO URGENT NEED TO CALL '/users/${user_id}/init'

def test_login_ok(unauthed_client, fresh_db, user):
    client = unauthed_client
    res = client.post('/auth', data=json.dumps({
        'email': user['email'],
        'password': user['password'],
    }))
    assert res.status_code == 200
    access_token = json.loads(res.data)['access_token']
    try:
        payload = jwt.decode(access_token, TOKEN_SECRET_KEY)
        uid = payload['uid']
        gid = payload['gid']
    except:
        pytest.fail('failed decoding access_token JWT!')
    try:
        uuid.UUID(uid, version=4)
        uuid.UUID(gid, version=4)
    except ValueError:
        pytest.fail('access_token\'s uid/gid claim is not valid UUID!')
    assert payload['gid'] is not None
    assert payload['iat'] is not None
    assert payload['exp'] is not None
    # TODO: assert token iat claim > now
    # TODO: assert token exp claim > now
    # TODO: assert token gid claim OK


def test_login_bad_email(unauthed_client, fresh_db, user):
    client = unauthed_client
    res = client.post('/auth', data=json.dumps({
        'email': 'clearly_not_an_email',
        'password': user['password'],
    }))
    assert res.status_code == 400
    res = client.post('/auth', data=json.dumps({
        'password': user['password'],
    }))
    assert res.status_code == 400


def test_login_nonexistent_email(unauthed_client, fresh_db):
    client = unauthed_client
    res = client.post('/auth', data=json.dumps({
        'email': 'this_email_neva_been_seen@befo.re',
        'password': 'irrelevantpassword',
    }))
    assert res.status_code == 404


def test_login_bad_password(unauthed_client, fresh_db, user):
    client = unauthed_client
    res = client.post('/auth', data=json.dumps({
        'email': user['email'],
        'password': 'not_the_user_password',
    }))
    assert res.status_code == 401
    res = client.post('/auth', data=json.dumps({
        'email': user['email'],
    }))
    assert res.status_code == 400


def test_auth_ok(unauthed_client, fresh_db, user):
    client = unauthed_client
    res = client.post('/auth', data=json.dumps({
        'email': user['email'],
        'password': user['password'],
    }))
    assert res.status_code == 200
    access_token = json.loads(res.data)['access_token']
    auth_hdr = {'Authorization': 'Bearer {}'.format(access_token)}
    res = client.get('/tasks', headers=auth_hdr)
    assert res.status_code == 200


def test_testing_auth_token(unauthed_client, fresh_db):
    client = unauthed_client
    testing_token_header = {'Authorization': 'Bearer master_key'}
    res = client.get('/tasks', headers=testing_token_header)
    assert res.status_code == 200


def test_hidden_auth_get(unauthed_client):
    client = unauthed_client
    query_string = {'access_token': 'Bearer 12345678910'}
    base_url = 'http://foo.example.com'
    res = client.get('/auth', query_string=query_string, base_url=base_url)
    assert res.status_code == 404
    res = client.get('/auth', base_url=base_url)
    assert res.status_code == 400


def test_auth_expired_token(unauthed_client, fresh_db, user):
    client = unauthed_client
    res = client.post('/auth', data=json.dumps({
        'email': user['email'],
        'password': user['password'],
    }))
    assert res.status_code == 200
    access_token = json.loads(res.data)['access_token']
    jwt_dict = jwt.decode(access_token, TOKEN_SECRET_KEY)
    jwt_dict['exp'] = datetime.utcnow() - timedelta(seconds=1)
    exp_access_token = jwt.encode(jwt_dict, TOKEN_SECRET_KEY)
    auth_hdr = {'Authorization': 'Bearer {}'.format(exp_access_token)}
    res = client.get('/tasks', headers=auth_hdr)
    assert res.status_code == 401


def test_auth_bad_token_signature(unauthed_client, fresh_db, user):
    client = unauthed_client
    res = client.post('/auth', data=json.dumps({
        'email': user['email'],
        'password': user['password'],
    }))
    assert res.status_code == 200
    access_token = json.loads(res.data)['access_token']
    hdr, payload, sig = access_token.split('.')
    sig = sig[:(len(sig)/3)] + 'x'*(len(sig)/3) + sig[(2*len(sig)/3):]
    bad_access_token = '.'.join([hdr, payload, sig])
    auth_hdr = {'Authorization': 'Bearer {}'.format(bad_access_token)}
    res = client.get('/tasks', headers=auth_hdr)
    assert res.status_code == 401


def test_auth_bad_token_no_uid(unauthed_client, fresh_db, user):
    client = unauthed_client
    res = client.post('/auth', data=json.dumps({
        'email': user['email'],
        'password': user['password'],
    }))
    assert res.status_code == 200
    access_token = json.loads(res.data)['access_token']
    jwt_dict = jwt.decode(access_token, TOKEN_SECRET_KEY)
    del jwt_dict['uid']
    bad_access_token = jwt.encode(jwt_dict, TOKEN_SECRET_KEY)
    auth_hdr = {'Authorization': 'Bearer {}'.format(bad_access_token)}
    res = client.get('/tasks', headers=auth_hdr)
    assert res.status_code == 401


def test_func_new_token():
    """ TODO """
    pass


def test_func_validate_token():
    """ TODO """
    pass


def test_func_hash_password():
    """ TODO """
    pass


def test_func_assert_valid_password():
    """ TODO """
    pass

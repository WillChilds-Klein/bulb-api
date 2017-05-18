import json
import pytest
import re
import uuid

from bulb_api.handlers import (
    create_entity,
    get_entity,
    list_entity,
    update_entity,
    delete_entity
)


with open(str(pytest.TEST_DATA_DIR / 'users.json')) as f:
    USERS = json.load(f)

with open(str(pytest.TEST_DATA_DIR / 'documents.json')) as f:
    DOCUMENTS = json.load(f)

with open(str(pytest.TEST_DATA_DIR / 'resources.json')) as f:
    RESOURCES = json.load(f)

with open(str(pytest.TEST_DATA_DIR / 'organizations.json')) as f:
    ORGANIZATIONS = json.load(f)


# +---------+
# | GENERAL |
# +---------+

def test_specify_bad_model():
    pass


# +--------+
# | CREATE |
# +--------+

def test_create_entity_ok(client):
    user = dict(USERS[1])
    res = client.post('/users', data=json.dumps(user),
                                content_type='application/json')
    assert res.status_code == 201


def test_create_entity_missing_attrs(client):
    user = dict(USERS[1])
    for attr in user.keys():
        bad_user = dict(user)   # make copy to fuck around with
        del bad_user[attr]      # fuck around with it
        res = client.post('/users', data=json.dumps(bad_user),
                                    content_type='application/json')
        assert res.status_code == 400


def test_create_entity_extra_attrs(client):
    bad_user = dict(USERS[1])
    bad_user['foo'] = 'yourmom'
    res = client.post('/users', data=json.dumps(bad_user),
                                content_type='application/json')
    assert res.status_code == 400


def test_create_entity_bad_attr_types(client):
    user = dict(USERS[1])
    for attr in user.keys():
        bad_user = dict(user)
        bad_user[attr] = None   # test data shouldn't include any nullables
        res = client.post('/users', data=json.dumps(bad_user),
                                    content_type='application/json')
        assert res.status_code == 400


def test_create_entity_already_exists(client):
    # TODO: implement this safety check in the actual code
    user = dict(USERS[1])
    res = client.post('/users', data=json.dumps(user),
                                content_type='application/json')
    assert res.status_code == 201
    res = client.post('/users', data=json.dumps(user),
                                content_type='application/json')
    assert res.status_code == 409


# TODO: parameterize all this shnit over ALL entity types
def test_read_newly_created(client):
    # TODO: change '*_id' to 'id'!!
    user = dict(USERS[1])
    res = client.post('/users', data=json.dumps(user),
                                content_type='application/json')
    assert res.status_code == 201
    user_id = json.loads(res.data)['user_id']
    user_id_is_valid = True
    try:
        uuid.UUID(user_id, version=4)
    except ValueError:
        user_id_is_valid = False
    assert user_id_is_valid
    res = client.get('/users/{user_id}'.format(user_id=user_id))
    assert res.status_code == 200
    res_data = json.loads(res.data)
    for attr in user.keys():
        assert res_data[attr]
        assert res_data[attr] == user[attr]


# +------+
# | READ |
# +------+

# TODO: create DDB fixture, and pre-populated it!
def test_get_entity_ok():
    pass


def test_get_entity_not_found():
    pass


def test_list_entity_ok():
    pass


# +--------+
# | UPDATE |
# +--------+

def test_update_entity_ok():
    pass


def test_update_entity_missing_attrs():
    pass


def test_update_entity_extra_attrs():
    pass


def test_update_entity_bad_attr_types():
    pass


# +--------+
# | DELETE |
# +--------+

def test_delete_entity_ok():
    pass


def test_delete_entity_not_found():
    pass

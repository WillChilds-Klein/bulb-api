import copy
import json
import logging
import os
import pytest
import uuid

from datetime import datetime
from connexion import App
from pathlib import Path

from bulb_api.auth import hash_password
from bulb_api.handlers import get_org_scoped_models, clean_response
from bulb_api.models import (
    BulbModel,
    Document,
    Organization,
    Resource,
    User,
    Task,
)


logging.basicConfig()

ROOT_DIR = Path(__file__).parent.parent
APP_DIR = ROOT_DIR / 'bulb_api'
SPEC_DIR = APP_DIR / 'spec'

TEST_DIR = Path(__file__).parent
DATA_DIR = TEST_DIR / 'test_data'


def dummy_data(entity_name, minimal=True):
        file_path = str(DATA_DIR
                        / Path('minimum_input' if minimal else 'full_input')
                        / Path(entity_name.lower() + '.json'))
        with open(file_path) as f:
            return json.load(f)


def get_client(app, access_token=None):
    class TestClientWrapper(object):
        """ Given a flask `app`, return ready-to-use test client.

        Sets `Content-Type` header for JSON for all requests made with returned
        clients. If `access_token` is non-None, all requests from the test
        client will specify that token in the `Authorization` HTTP header as a
        OAuth "Bearer" token. Inspired by this S/O post: http://bit.ly/2tnhCeY
        """
        def __init__(self, app):
            self.app = app
        def __call__(self, environ, start_response):
            environ['CONTENT_TYPE'] = 'application/json'
            if access_token:
                environ['HTTP_AUTHORIZATION'] = 'Bearer {}'.format(access_token)
            return self.app(environ, start_response)
    app.wsgi_app = TestClientWrapper(app.wsgi_app)
    with app.test_client(use_cookies=False) as client:
        yield client


@pytest.fixture(scope='function')
def fresh_db():
    # NOTE: assumes ddb is running locally on port 8000
    models = BulbModel.__subclasses__()
    for model in models:
        if model.exists():
            model.delete_table()
        model.create_table()
    yield   # ^--setup | teardown --v
    for model in models:
        model.delete_table()


# TODO: move all this shit to a test config...
@pytest.fixture(scope='function')
def app():
    from bulb_api import start_auth_thread
    start_auth_thread(port=8081)
    os.environ['TOKENINFO_URL'] = 'http://localhost:8081/auth'
    cxn_app = App(__name__, port=8082, specification_dir=SPEC_DIR)
    cxn_app.add_api('swagger.yaml', validate_responses=True,
                                    strict_validation=True)
    cxn_app.app.testing = True
    return cxn_app.app


@pytest.fixture(scope='function')
def unauthed_client(app):
    return next(get_client(app))


@pytest.fixture(scope='function', params=get_org_scoped_models())
def model(request):
    return request.param


@pytest.fixture(scope='function')
def dummy_entities():
    models = get_org_scoped_models()
    data = {
        model: dummy_data(model.__name__) for model in models
    }
    return data


@pytest.fixture(scope='function')
def user(unauthed_client):
    user = dummy_data(User.__name__)[0]
    res = unauthed_client.post('/users', data=json.dumps(user))
    assert res.status_code == 201
    user_data = json.loads(res.data)
    user_data['password'] = user['password']
    return user_data


@pytest.fixture(scope='function')
def initd_user(unauthed_client, user):
    user_id = user['user_id']
    res = unauthed_client.post('/users/{user_id}/init'.format(user_id=user_id))
    assert res.status_code == 201
    user_data = json.loads(res.data)
    return user_data


@pytest.fixture(scope='function')
def access_token(user, unauthed_client):
    auth_data = {'email': user['email'], 'password': user['password']}
    res = unauthed_client.post('/auth', data=json.dumps(auth_data))
    res_data = json.loads(res.data)
    return res_data['access_token']


@pytest.fixture(scope='function')
def client(app, access_token):
    return next(get_client(app, access_token=access_token))


@pytest.fixture(scope='function')
def entities(user, dummy_entities):
    entities = {}
    for model in dummy_entities.keys():
        new_entities = []
        if model is User:
            new_entity = copy.deepcopy(user)
            new_entity.pop('create_datetime', None)
            new_entities.append(new_entity)
        else:
            for dummy_entity in dummy_entities[model]:
                new_entity = copy.deepcopy(dummy_entity)
                new_entity['org_id'] = copy.copy(user['org_id'])
                new_entities.append(new_entity)
        entities[model] = sorted(new_entities)
    return entities


@pytest.fixture(scope='function')
def entity_ids(entities):
    ids = {
        model: [str(uuid.uuid4()) for _ in ents]
        for model, ents in entities.iteritems()
    }
    ids[User] = [entities[User][0]['user_id']]  # always take User's real id
    return ids


@pytest.fixture(scope='function')
def prepop_db(fresh_db, user, entities, entity_ids):
    prepop_models = filter(lambda m: m not in [User, Organization],
                           entities.keys())
    for model in prepop_models:
        for entity, entity_id in zip(entities[model], entity_ids[model]):
            entity_item = model(entity_id)
            entity_item.update_from_dict(entity)
            entity_item.create_datetime = datetime.utcnow()
            entity_item.save()

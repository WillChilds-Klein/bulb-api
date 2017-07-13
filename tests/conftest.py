import json
import logging
import os
import pytest
import uuid

from datetime import datetime
from connexion import App
from pathlib import Path

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

ORG_OWNED_ENTITIES = [
    User,
    Task,
    Document,
]


@pytest.fixture(scope='function', params=BulbModel.__subclasses__())
def model(request):
    return request.param


@pytest.fixture(scope='session')
def dummy_entities():
    def dummy_data(entity_name, minimal=True):
        file_path = str(DATA_DIR
                        / Path('minimum_input' if minimal else 'full_input')
                        / Path(entity_name.lower() + '.json'))
        with open(file_path) as f:
            return json.load(f)
    models = BulbModel.__subclasses__()
    data = {
        model: dummy_data(model.__name__) for model in models
    }
    return data


@pytest.fixture(scope='function')
def entities(model, dummy_entities):
    return sorted([dict(entity) for entity in dummy_entities[model]])


@pytest.fixture(scope='function')
def entity_ids(entities):
    return [str(uuid.uuid4()) for _ in entities]


@pytest.fixture(scope='function')
def org_owned_entities(entities):
    return filter(lambda e: e in ORG_OWNED_ENTITIES, entities)


@pytest.fixture(scope='function')
def fresh_db():
    # NOTE: assumes ddb is running locally on port 8000
    # TODO: implement this to be independent of pynamodb?
    models = [Document, Organization, Resource, User, Task]
    for model in models:
        if model.exists():
            model.delete_table()
        model.create_table()
    yield   # ^--setup | teardown --v
    for model in models:
        model.delete_table()


@pytest.fixture(scope='function')
def prepop_db(fresh_db, model, entities, entity_ids):
    for entity, entity_id in zip(entities, entity_ids):
        # user is special case due to password(_hash) sanitization/etc.
        if model is User:
            from bulb_api.handlers import create_user
            # make copies of entity/entity_id to avoid mutative side effects.
            _ , st = create_user(dict(entity), user_id=str(entity_id))
            assert st == 201
        else:
            entity_item = model(entity_id)
            entity_item.update_from_dict(entity)
            entity_item.create_datetime = datetime.utcnow()
            entity_item.save()


@pytest.fixture(scope='session')
def user():
    return {
        'name': 'bob',
        'email': 'bob@bulb.co',
        'password': 'abcd1234',
    }


# TODO: move all this shit to a test config...
@pytest.fixture(scope='session')
def app():
    from bulb_api import start_auth_thread
    start_auth_thread(port=8081)
    os.environ['TOKENINFO_URL'] = 'http://localhost:8081/auth'
    cxn_app = App(__name__, port=8082, specification_dir=SPEC_DIR)
    cxn_app.add_api('swagger.yaml', validate_responses=True,
                                    strict_validation=True)
    cxn_app.app.testing = True
    return cxn_app.app


def get_client(app, access_token=None):
    class AuthenticatedTestClientWrapper(object):
        """ Inspired by this S/O post: http://bit.ly/2tnhCeY
        """
        def __init__(self, app):
            self.app = app
        def __call__(self, environ, start_response):
            environ['CONTENT_TYPE'] = 'application/json'
            if access_token:
                environ['HTTP_AUTHORIZATION'] = 'Bearer {}'.format(access_token)
            return self.app(environ, start_response)
    app.wsgi_app = AuthenticatedTestClientWrapper(app.wsgi_app)
    with app.test_client(use_cookies=False) as client:
        yield client


@pytest.fixture(scope='module')
def client(app):
    return next(get_client(app, access_token='master_key'))


@pytest.fixture(scope='module')
def unauthed_client(app):
    return next(get_client(app))


@pytest.fixture(scope='function')
def authorized_client(app, unauthed_client, user):
    # TODO: make unauth'd client the default, update where needed...
    res = unauthed_client.post('/user', data=json.dumps(user))
    assert res.status == 201
    auth_data = {'email': user['email'], 'password': user['password']}
    res = unauthed_client.post('/auth', data=json.dumps(auth_data))
    access_token = res.data['access_token']
    return next(get_client(app, access_token=access_token))


@pytest.fixture(scope='function')
def authorized_entities(authorized_client, fresh_db, org_owned_entities):
    # TODO: this fixture should populate the db with org_owned_entities
    #       instances owned by authorized_client's user and its org_id.
    pass

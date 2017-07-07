import json
import logging
import os
import pytest
import time

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

CONSTANTS = {
    'TEST_DATA_DIR': DATA_DIR
}


def dummy_data(entity_name, minimal=True):
    file_path = str(pytest.TEST_DATA_DIR
                    / Path('minimum_input' if minimal else 'full_input')
                    / Path(entity_name.lower() + '.json'))
    with open(file_path) as f:
        return json.load(f)


@pytest.fixture(scope='session')
def dummy_entities():
    models = BulbModel.__subclasses__()
    data = {
        model: dummy_data(model.__name__) for model in models
    }
    return data


@pytest.fixture(scope='module')
def pytest_namespace():
    return CONSTANTS


# TODO: move all this shit to a test config...
@pytest.fixture(scope='module')
def client():
    from bulb_api import start_auth_thread
    start_auth_thread(port=8081)
    os.environ['TOKENINFO_URL'] = 'http://localhost:8081/auth'
    class AuthenticatedTestClientWrapper(object):
        """ Inspired by this S/O post: http://bit.ly/2tnhCeY
        """
        def __init__(self, app):
            self.app = app
        def __call__(self, environ, start_response):
            environ['HTTP_AUTHORIZATION'] = 'Bearer master_key'
            return self.app(environ, start_response)
    cxn_app = App(__name__, port=8082, specification_dir=SPEC_DIR)
    cxn_app.add_api('swagger.yaml', validate_responses=True)
                                    # strict_validation=True)
    cxn_app.app.wsgi_app = AuthenticatedTestClientWrapper(cxn_app.app.wsgi_app)
    cxn_app.app.testing = True
    with cxn_app.app.test_client(use_cookies=False) as client:
        yield client


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

import json
import logging
import pathlib
import pytest

from connexion import App


logging.basicConfig()

ROOT_DIR = pathlib.Path(__file__).parent.parent
APP_DIR = ROOT_DIR / 'bulb_api'
SPEC_DIR = APP_DIR / 'spec'

TEST_DIR = pathlib.Path(__file__).parent
DATA_DIR = TEST_DIR / 'test_data'

CONSTANTS = {
    'TEST_DATA_DIR': DATA_DIR
}

def pytest_namespace():
    return CONSTANTS


def create_test_app():
    cxn_app = App(__name__, port=8081, specification_dir=SPEC_DIR, debug=True)
    cxn_app.add_api('swagger.yaml', validate_responses=True)
    return cxn_app


@pytest.fixture(scope='module')
def client():
    return create_test_app().app.test_client(use_cookies=False)

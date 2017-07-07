import connexion
# import logging
import threading

from flask_cors import CORS

from .models import Document, Organization, Resource, User, Task


def create_app():
    connexion_app = connexion.App(__name__)
    connexion_app.add_api('spec/swagger.yaml', strict_validation=True,
                                               validate_responses=True)
    app = connexion_app.app

    app.config.from_pyfile('./config.py')

    # supp_creds for allowing cookie/auth headers to be passed. still need to
    # implement CSRF protection though... <-- TODO
    CORS(app, **app.config['CORS_CFG'])

    # logging.basicConfig(level=logging.INFO if not app.debug else logging.DEBUG)   # NOQA

    # TODO: move this to some init_app function so this isn't being called on
    #       startup every time.
    for model in Document, Organization, Resource, User, Task:
        if not model.exists():
            model.create_table()

    return app


def start_auth_thread(port=None):
    auth_app = create_app()
    auth_app.debug = False
    kwargs = {'host': 'localhost',
              'port': port if port else auth_app.config['AUTH_PORT']}
    auth_thread = threading.Thread(target=auth_app.run, kwargs=kwargs)
    auth_thread.daemon = True   # needed to ensure automatic cleanup on exit.
    auth_thread.start()
    return auth_app, auth_thread


auth_app, _ = start_auth_thread()
app = create_app()

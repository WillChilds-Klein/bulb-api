import connexion

from flask_cors import CORS

from .models import Document, Organization, Resource, User


def create_app(cfg_path=None):
    connexion_app = connexion.App(__name__)
    connexion_app.add_api('spec/swagger.yaml', strict_validation=True,
                                               validate_responses=True)
    app = connexion_app.app

    app.config.from_pyfile('./default_config.py')

    # supp_creds for allowing cookie/auth headers to be passed. still need to
    # implement CSRF protection though... <-- TODO
    CORS(app, supports_credentials=True)

    # TODO: move this to some init_app function so this isn't being called on
    #       startup every time.
    for model in Document, Organization, Resource, User:
        if not model.exists():
            model.create_table()

    return app


app = create_app()

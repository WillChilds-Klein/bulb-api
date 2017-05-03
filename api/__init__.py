import connexion

from .models import Document, Organization, Resource, User


def create_app(cfg_path=None):
    connexion_app = connexion.App(__name__)
    connexion_app.add_api('spec/swagger.yaml', strict_validation=True,
                                               validate_responses=True)
    app = connexion_app.app

    app.config.from_pyfile('./default_config.py')

    # TODO: move this to some init_app function so this isn't being called on
    #       startup every time.
    for model in Document, Organization, Resource, User:
        if not model.exists():
            model.create_table()

    return app


app = create_app()

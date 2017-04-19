import connexion


def create_app(cfg_path=None):
    connexion_app = connexion.App(__name__)
    connexion_app.add_api('spec/swagger.yaml', strict_validation=True,
                                               validate_responses=True)
    app = connexion_app.app

    return app


app = create_app()

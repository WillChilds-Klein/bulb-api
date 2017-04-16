import connexion

from connexion import NoContent


org_db = {}
doc_db = {}
user_db = {}


def get_organization(id):
    org_id = id
    print org_id, type(org_id)
    print [type(key) for key in org_db.keys()]
    if org_id in org_db:
        return org_db[id], 200
    return NoContent, 404


def update_organization(body, id):
    org_id = body['id']
    if org_id in org_db:
        org_db[org_id] = body
        return NoContent, 200
    return NoContent, 404


def delete_organization(id):
    org_id = id
    if org_id in org_db:
        del org_db[org_id]
        return NoContent, 200
    return NoContent, 404


def list_organizations():
    return org_db.values()


def create_organization(body):
    org_id = body['id']
    org_db[org_id] = body
    return 'Success!', 200


def get_document(id):
    doc_id = id
    if doc_id in doc_db:
        return doc_db[id], 200
    return NoContent, 404


def update_document(body, id):
    doc_id = body['id']
    if doc_id in doc_db:
        doc_db[doc_id] = body
        return NoContent, 200
    return NoContent, 404


def delete_document(id):
    doc_id = id
    if doc_id in doc_db:
        del doc_db[doc_id]
        return NoContent, 200
    return NoContent, 404


def list_documents():
    return doc_db.values()


def create_document(body):
    doc_id = body['id']
    doc_db[doc_id] = body
    return 'Success!', 200


def get_user(id):
    user_id = id
    print user_id, type(user_id)
    print [type(key) for key in user_db.keys()]
    if user_id in user_db:
        return user_db[id], 200
    return NoContent, 404


def update_user(body, id):
    user_id = body['id']
    if user_id in user_db:
        user_db[user_id] = body
        return NoContent, 200
    return NoContent, 404


def delete_user(id):
    user_id = id
    if user_id in user_db:
        del user_db[user_id]
        return NoContent, 200
    return NoContent, 404


def list_users():
    return user_db.values()


def create_user(body):
    user_id = body['id']
    user_db[user_id] = body
    return 'Success!', 200


connexion_app = connexion.App(__name__)
connexion_app.add_api('spec/swagger.yaml', strict_validation=True,
                                           validate_responses=True)

app = connexion_app.app

if __name__ == '__main__':
    connexion_app.run(port=8080, host='0.0.0.0')

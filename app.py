import connexion

from connexion import NoContent
from datetime import datetime
from uuid import uuid4


org_db = {}
doc_db = {}
user_db = {}

DATETIME_FMT = '%Y-%m-%dT%H:%M:%SZ'


def get_organization(org_id):
    if org_id in org_db:
        return org_db[org_id], 200
    return NoContent, 404


def update_organization(body, org_id):
    if org_id in org_db:
        org_db[org_id].update(body)
        return org_db[org_id], 200
    return NoContent, 404


def delete_organization(org_id):
    if org_id in org_db:
        del org_db[org_id]
        return NoContent, 200
    return NoContent, 404


def list_organizations():
    return org_db.values()


def create_organization(body):
    org_id = str(uuid4())
    body['org_id'] = org_id
    body['create_datetime'] = datetime.utcnow().strftime(DATETIME_FMT)
    org_db[org_id] = body
    return org_db[org_id], 200


def get_document(doc_id):
    if doc_id in doc_db:
        return doc_db[doc_id], 200
    return NoContent, 404


def update_document(body, doc_id):
    if doc_id in doc_db:
        doc_db[doc_id].update(body)
        return doc_db[doc_id], 200
    return NoContent, 404


def delete_document(doc_id):
    if doc_id in doc_db:
        del doc_db[doc_id]
        return NoContent, 200
    return NoContent, 404


def list_documents():
    return doc_db.values()


def create_document(body):
    doc_id = str(uuid4())
    body['doc_id'] = doc_id
    body['create_datetime'] = datetime.utcnow().strftime(DATETIME_FMT)
    doc_db[doc_id] = body
    return doc_db[doc_id], 200


def get_user(user_id):
    if user_id in user_db:
        return user_db[user_id], 200
    return NoContent, 404


def update_user(body, user_id):
    if user_id in user_db:
        user_db[user_id].update(body)
        return user_db[user_id], 200
    return NoContent, 404


def delete_user(user_id):
    if user_id in user_db:
        del user_db[user_id]
        return NoContent, 200
    return NoContent, 404


def list_users():
    return user_db.values()


def create_user(body):
    user_id = str(uuid4())
    body['user_id'] = user_id
    body['create_datetime'] = datetime.utcnow().strftime(DATETIME_FMT)
    user_db[user_id] = body
    return user_db[user_id], 200


def get_resource(res_id):
    if res_id in resource_db:
        return resource_db[res_id], 200
    return NoContent, 404


def update_resource(body, res_id):
    if res_id in resource_db:
        resource_db[res_id].update(body)
        return resource_db[res_id], 200
    return NoContent, 404


def delete_resource(res_id):
    if res_id in resource_db:
        del resource_db[res_id]
        return NoContent, 200
    return NoContent, 404


def list_resources():
    return resource_db.values()


def create_resource(body):
    res_id = str(uuid4())
    body['res_id'] = res_id
    body['create_datetime'] = datetime.utcnow().strftime(DATETIME_FMT)
    resource_db[res_id] = body
    return resource_db[res_id], 200


connexion_app = connexion.App(__name__)
connexion_app.add_api('spec/swagger.yaml', strict_validation=True,
                                           validate_responses=True)

app = connexion_app.app

if __name__ == '__main__':
    connexion_app.run(port=8080, host='0.0.0.0')

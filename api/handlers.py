from connexion import NoContent
from datetime import datetime
from pynamodb.exceptions import DeleteError
from uuid import uuid4

from .models import User


org_db = {}
doc_db = {}
res_db = {}

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
    return org_db.values(), 200


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
    return doc_db.values(), 200


def create_document(body):
    doc_id = str(uuid4())
    body['doc_id'] = doc_id
    body['create_datetime'] = datetime.utcnow().strftime(DATETIME_FMT)
    doc_db[doc_id] = body
    return doc_db[doc_id], 200


def get_user(user_id):
    try:
        return User.get(user_id).to_dict(), 200
    except User.DoesNotExist:
        return NoContent, 404


def update_user(body, user_id):
    try:
        user = User.get(user_id)
    except User.DoesNotExist:
        return NoContent, 404
    user.update_from_dict(body)
    user.save()
    return user.to_dict(), 200


def delete_user(user_id):
    try:
        User.get(user_id).delete()
    except DeleteError:
        return NoContent, 404
    return NoContent, 200


def list_users():
    users = [user.to_dict() for user in User.scan()]
    return users, 200


def create_user(body):
    user = User(User.get_unused_uuid())
    user.init_from_dict(body)
    user.create_datetime = datetime.utcnow()
    user.save()
    return user.to_dict(), 200


def get_resource(res_id):
    if res_id in res_db:
        return res_db[res_id], 200
    return NoContent, 404


def update_resource(body, res_id):
    if res_id in res_db:
        res_db[res_id].update(body)
        return res_db[res_id], 200
    return NoContent, 404


def delete_resource(res_id):
    if res_id in res_db:
        del res_db[res_id]
        return NoContent, 200
    return NoContent, 404


def list_resources():
    return res_db.values(), 200


def create_resource(body):
    res_id = str(uuid4())
    body['res_id'] = res_id
    body['create_datetime'] = datetime.utcnow().strftime(DATETIME_FMT)
    res_db[res_id] = body
    return res_db[res_id], 200

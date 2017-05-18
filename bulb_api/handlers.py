from connexion import NoContent
from datetime import datetime
from pynamodb.exceptions import DeleteError

from .models import BulbModel, Document, Organization, Resource, User


DATETIME_FMT = '%Y-%m-%dT%H:%M:%SZ'


def get_organization(org_id):
    return get_entity(Organization, org_id)


def update_organization(body, org_id):
    return update_entity(Organization, org_id, body)


def delete_organization(org_id):
    return delete_entity(Organization, org_id)


def list_organizations():
    return list_entity(Organization)


def create_organization(body):
    return create_entity(Organization, body)


def get_document(doc_id):
    return get_entity(Document, doc_id)


def update_document(body, doc_id):
    return update_entity(Document, doc_id, body)


def delete_document(doc_id):
    return delete_entity(Document, doc_id)


def list_documents():
    return list_entity(Document)


def create_document(body):
    return create_entity(Document, body)


def get_user(user_id):
    return get_entity(User, user_id)


def update_user(body, user_id):
    return update_entity(User, user_id, body)


def delete_user(user_id):
    return delete_entity(User, user_id)


def list_users():
    return list_entity(User)


def create_user(body):
    return create_entity(User, body)


def get_resource(res_id):
    return get_entity(Resource, res_id)


def update_resource(body, res_id):
    return update_entity(Resource, res_id, body)


def delete_resource(res_id):
    return delete_entity(Resource, res_id)


def list_resources():
    return list_entity(Resource)


def create_resource(body):
    return create_entity(Resource, body)


def create_entity(model, body):
    if not issubclass(model, BulbModel):
        raise Exception('`model` must be subclass of BulbModel!')
    entity = model(model.get_unused_uuid())
    entity.update_from_dict(body)
    entity.create_datetime = datetime.utcnow()
    try:
        entity.save()
    except ValueError as e:
        return e.message, 400
    return entity.to_dict(), 201


def get_entity(model, entity_id):
    if not issubclass(model, BulbModel):
        raise Exception('`model` must be subclass of BulbModel!')
    try:
        return model.get(entity_id).to_dict(), 200
    except model.DoesNotExist:
        return NoContent, 404


def list_entity(model):
    if not issubclass(model, BulbModel):
        raise Exception('`model` must be subclass of BulbModel!')
    entities = [entity.to_dict() for entity in model.scan()]
    return entities, 200


def update_entity(model, entity_id, body):
    if not issubclass(model, BulbModel):
        raise Exception('`model` must be subclass of BulbModel!')
    try:
        entity = model.get(entity_id)
    except model.DoesNotExist:
        return NoContent, 404
    entity.update_from_dict(body)
    entity.save()
    return entity.to_dict(), 200


def delete_entity(model, entity_id):
    if not issubclass(model, BulbModel):
        raise Exception('`model` must be subclass of BulbModel!')
    try:
        model.get(entity_id).delete()
    except DeleteError:
        return NoContent, 404
    return NoContent, 200

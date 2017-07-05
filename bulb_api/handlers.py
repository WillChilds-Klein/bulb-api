from connexion import NoContent
from datetime import datetime

from .auth import hash_password, assert_valid_password
from .config import HIDDEN_ATTRIBUTES
from .models import BulbModel, Document, Organization, Resource, User


def get_organization(org_id):
    return get_entity(Organization, org_id)


def update_organization(body, org_id):
    return update_entity(Organization, org_id, body)


def delete_organization(org_id):
    return delete_entity(Organization, org_id)


def list_organizations(offset=0, limit=None):
    return list_entity(Organization, offset, limit)


def create_organization(body):
    return create_entity(Organization, body)


def get_document(doc_id):
    return get_entity(Document, doc_id)


def update_document(body, doc_id):
    return update_entity(Document, doc_id, body)


def delete_document(doc_id):
    return delete_entity(Document, doc_id)


def list_documents(offset=0, limit=None):
    return list_entity(Document, offset, limit)


def create_document(body):
    return create_entity(Document, body)


def get_user(user_id):
    return get_entity(User, user_id)


def update_user(body, user_id):
    try:
        password = body.pop('password')     # get passwd and delete from dict.
        assert_valid_password(password)
        body['password_hash'] = hash_password(password)
    except KeyError:                        # key 'password' not in body
        pass
    except AssertionError:                  # passwd validity assertion failed
        return 'Invalid password!', 400
    return update_entity(User, body)


def delete_user(user_id):
    return delete_entity(User, user_id)


def list_users(offset=0, limit=None):
    return list_entity(User, offset, limit)


def create_user(body):
    # TODO: perhaps move this logic and analog in update_user to User model?
    try:
        password = body.pop('password')     # get passwd and delete from dict.
        assert_valid_password(password)
    except KeyError:                        # user didn't specify a password.
        return 'Please specify a password in the body!', 400
    except AssertionError:                  # user specified invalid password.
        return 'Invalid password!', 400
    body['password_hash'] = hash_password(password)
    body['organization'] = Organization.get_unused_uuid()  # 1:1 user -> org
    return create_entity(User, body)


def get_resource(res_id):
    return get_entity(Resource, res_id)


def update_resource(body, res_id):
    return update_entity(Resource, res_id, body)


def delete_resource(res_id):
    return delete_entity(Resource, res_id)


def list_resources(offset=0, limit=None):
    return list_entity(Resource, offset, limit)


def create_resource(body):
    return create_entity(Resource, body)


def clean_response(body):
    return dict([(k, v) for (k, v) in body.iteritems()
                                 if k not in HIDDEN_ATTRIBUTES])


def create_entity(model, body):
    if not issubclass(model, BulbModel):
        raise Exception('`model` must be subclass of BulbModel!')
    if model().get_hash_key_name() in body.keys():
        return 'Cannot specify hash_key in POST body!', 400
    entity = model(hash_key=model.get_unused_uuid())
    entity.update_from_dict(body)
    entity.create_datetime = datetime.utcnow()
    try:
        entity.save()
    except ValueError as e:
        return e.message, 400
    return clean_response(entity.to_dict()), 201


def get_entity(model, entity_id):
    if not issubclass(model, BulbModel):
        raise Exception('`model` must be subclass of BulbModel!')
    try:
        entity = model.get(entity_id).to_dict()
    except model.DoesNotExist:
        return NoContent, 404
    return clean_response(entity), 200


def list_entity(model, offset, limit):
    if not issubclass(model, BulbModel):
        raise Exception('`model` must be subclass of BulbModel!')
    # TODO: this is pretty unscalable... :(
    # b/c pynamo represents index/models query/scan results as iterators, we're
    # going to have to manually iterate over the totality of that iterator
    # until we get to the appropriate offset, then start aggregating the return
    # list. see:
    # https://stackoverflow.com/questions/39671167/index-into-a-python-iterator
    # https://github.com/pynamodb/PynamoDB/pull/48
    entities = [entity.to_dict() for entity in model.scan()]
    if offset > len(entities):  # TODO add test case where offset == len...
        return 'Offset larger than number of available entities!', 400
    try:
        offset, limit = (int(offset), int(limit) if limit else None)
    except ValueError:  # TODO: add CRUD test case around this.
        return 'Offset and limit must be integers!'
    cleaned_entities = [clean_response(d) for d in entities[offset:][:limit]]
    return cleaned_entities, 200


def update_entity(model, entity_id, body):
    # TODO make decorator for custom input validation?
    if not issubclass(model, BulbModel):
        raise Exception('`model` must be subclass of BulbModel!')
    if model().get_hash_key_name() in body.keys():
        return 'Cannot specify hash_key in PUT body!', 400
    try:
        entity = model.get(entity_id)
    except model.DoesNotExist:
        return NoContent, 404
    entity.update_from_dict(body)
    try:
        entity.save()
    except ValueError as e:
        return e.message, 400
    return clean_response(entity.to_dict()), 200


def delete_entity(model, entity_id):
    if not issubclass(model, BulbModel):
        raise Exception('`model` must be subclass of BulbModel!')
    try:
        model.get(entity_id).delete()
    except model.DoesNotExist:
        return NoContent, 404
    return NoContent, 200

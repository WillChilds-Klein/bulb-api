import flask

from connexion import NoContent
from connexion.exceptions import ProblemException
from datetime import datetime

from .auth import hash_password, assert_valid_password
from .config import HIDDEN_ATTRIBUTES, MASTER_KEY_UID, MASTER_KEY_GID
from .default_tasks import DEFAULT_TASKS
from .exceptions import BulbException
from .models import BulbModel, Document, Organization, Resource, User, Task


def get_organization(org_id):
    return get_entity(Organization, org_id)


def update_organization(body, org_id):
    return update_entity(Organization, org_id, body)


def delete_organization(org_id):
    return delete_entity(Organization, org_id)


def list_organizations(offset=0, limit=None):
    return list_entity(Organization, offset, limit)


def create_organization(body, org_id=None):
    return create_entity(Organization, body, entity_id=org_id, org_id=org_id)


def get_document(doc_id):
    return get_entity(Document, doc_id)


def update_document(body, doc_id):
    return update_entity(Document, doc_id, body)


def delete_document(doc_id):
    return delete_entity(Document, doc_id)


def list_documents(offset=0, limit=None):
    return list_entity(Document, offset, limit)


def create_document(body, org_id=None):
    return create_entity(Document, body, org_id=org_id)


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
    return update_entity(User, user_id, body)


def delete_user(user_id):
    return delete_entity(User, user_id)


def list_users(offset=0, limit=None):
    return list_entity(User, offset, limit)


def create_user(body, user_id=None):
    # TODO: perhaps move this logic and analog in update_user to User model?
    try:
        password = body.pop('password')     # get passwd and delete from dict.
        assert_valid_password(password)
    except KeyError:                        # user didn't specify a password.
        return 'Please specify a password in the body!', 400
    except AssertionError:                  # user specified invalid password.
        return 'Invalid password!', 400
    body['password_hash'] = hash_password(password)
    user_id = User.get_unused_uuid()
    org_id = Organization.get_unused_uuid()     # 1:1 user->org
    org_data = {'users': [user_id]}
    res, code = create_organization(org_data, org_id=org_id)
    if code != 201:
        raise BulbException('Failed to create Organization - code: {} msg: {}'
                            .format(str(code), str(res)))
    return create_entity(User, body, entity_id=user_id, org_id=org_id)


def init_user(user_id):
    try:
        user = User.get(user_id)
    except:
        raise BulbException('Failed to get user {}!'.format(user_id))
    org_id = user.org_id
    for task_body in DEFAULT_TASKS:
        res, code = create_task(task_body, org_id=org_id)
        if code != 201:
            raise BulbException('Failed mk Task - code: {} msg: {} task: {}'
                                .format(str(code), str(res), str(task_body)))
    return clean_response(user.to_dict()), 201


def get_resource(res_id):
    return get_entity(Resource, res_id)


def update_resource(body, res_id):
    return update_entity(Resource, res_id, body)


def delete_resource(res_id):
    return delete_entity(Resource, res_id)


def list_resources(offset=0, limit=None):
    return list_entity(Resource, offset, limit)


def create_resource(body, org_id=None):
    return create_entity(Resource, body, org_id=org_id)


def get_task(task_id):
    return get_entity(Task, task_id)


def update_task(body, task_id):
    return update_entity(Task, task_id, body)


def delete_task(task_id):
    return delete_entity(Task, task_id)


def list_tasks(offset=0, limit=None):
    return list_entity(Task, offset, limit)


def create_task(body, org_id=None):
    """ TODO: use pynamodb's `batch_write` mechanism here. """
    return create_entity(Task, body, org_id=org_id)


def clean_response(body):
    return dict([(k, v) for (k, v) in body.iteritems()
                                 if k not in HIDDEN_ATTRIBUTES
                                    and v is not None])


def get_uid():
    try:
        return flask.request.token_info.get('uid')
    except (AttributeError, RuntimeError):
        return None


def get_gid():
    try:
        return flask.request.token_info.get('gid')
    except (AttributeError, RuntimeError):
        return None


def get_org_scoped_models():
    """ Get list of models OrgIndex (models with attr named 'org_index'). """
    # TODO: be more precise than this. filtering on property name is dangerous
    return filter(lambda m: hasattr(m, 'org_index'),
                  BulbModel.__subclasses__())


def check_ownership(model, entity_id):
    uid, gid = get_uid(), get_gid()
    if uid == MASTER_KEY_UID and gid == MASTER_KEY_GID:
        return uid, gid
    try:
        entity = model.get(entity_id)
    except model.DoesNotExist:
        raise ProblemException(status=404, title='Not Found')
    try:
        detail = 'not authorized to access this resource'
        if entity.org_id != gid:
            raise ProblemException(status=403, title='Not Authorized',
                                               detail=detail)
        elif model is User and entity_id != uid:
            raise ProblemException(status=403, title='Not Authorized',
                                               detail=detail)
    except AttributeError as e:
        raise ProblemException(status=401, title='Unauthorized',
                                           detail=e.message())
    return uid, gid


def create_entity(model, body, entity_id=None, org_id=None):
    """ A generic function for creating a bulb Entity.

    NOTE: entity_id should be used for testing ONLY. In normal operation, we
    generate and assign the entity_id here.
    """
    if not issubclass(model, BulbModel):
        raise BulbException('Model {} must be subclass of BulbModel!'
                            .format(model.__name__))
    if model().get_hash_key_name() in body.keys():
        return 'Cannot specify hash_key in POST body!', 400
    if Organization().get_hash_key_name() in body.keys():
        return 'Cannot specify org_id in POST body!', 400
    entity = model(hash_key=entity_id if entity_id
                                      else model.get_unused_uuid())
    # if applicable, use org_id if specified, falling back to auth'd "gid"
    if model in get_org_scoped_models():
        entity.org_id = org_id if org_id else get_gid() if get_gid() else None
    entity.create_datetime = datetime.utcnow()
    try:
        entity.update_from_dict(body)
    except BulbException as e:
        return e.message, 400
    try:
        entity.save()
    except ValueError as e:
        return e.message, 400
    return clean_response(entity.to_dict()), 201


def get_entity(model, entity_id):
    if not issubclass(model, BulbModel):
        raise BulbException('Model {} must be subclass of BulbModel!'
                            .format(model.__name__))
    check_ownership(model, entity_id)
    try:
        entity = model.get(entity_id).to_dict()
    except model.DoesNotExist:
        return NoContent, 404
    return clean_response(entity), 200


def list_entity(model, offset, limit):
    if not issubclass(model, BulbModel):
        raise BulbException('Model {} must be subclass of BulbModel!'
                            .format(model.__name__))
    # TODO: this is pretty unscalable... :(
    # b/c pynamo represents index/models query/scan results as iterators, we're
    # going to have to manually iterate over the totality of that iterator
    # until we get to the appropriate offset, then start aggregating the return
    # list. see:
    # https://stackoverflow.com/questions/39671167/index-into-a-python-iterator
    # https://github.com/pynamodb/PynamoDB/pull/48
    uid, gid = get_uid(), get_gid()
    entities = None
    if uid == MASTER_KEY_UID and gid == MASTER_KEY_GID:
        entities = [entity.to_dict() for entity in model.scan()]
    elif model is Organization:
        entities = [model.get(gid).to_dict()]
    elif model in get_org_scoped_models() or model is User:
        entities = [ent.to_dict() for ent in model.org_index.query(gid)]
    if offset > len(entities):
        return 'Offset larger than number of available entities!', 400
    try:
        offset, limit = (int(offset), None if limit is None else int(limit))
    except ValueError:
        return 'Offset and limit must be integers!', 400
    cleaned_entities = [clean_response(d) for d in entities[offset:][:limit]]
    return cleaned_entities, 200


def update_entity(model, entity_id, body):
    # TODO: [URGENT] need to strip out immutable attrs (create_datetime, *_id,
    # etc.)
    if not issubclass(model, BulbModel):
        raise BulbException('Model {} must be subclass of BulbModel!'
                            .format(model.__name__))
    _, gid = check_ownership(model, entity_id)
    entity_id_key = model().get_hash_key_name()
    if entity_id_key in body.keys():
        if body[entity_id_key] != entity_id:
            msg = '{model_name} ID specified in body differs from ID in path.'
            return msg.format(model_name=model.__name__), 400
        else:
            del body[model().get_hash_key_name()]
    if 'org_id' in body.keys() and gid and gid != body['org_id']:
        return 'Specified org_id doesn\'t match user\'s gid!', 400
    try:
        entity = model.get(entity_id)
    except model.DoesNotExist:
        return NoContent, 404
    try:
        entity.update_from_dict(body)
    except BulbException as e:
        return e.message, 400
    try:
        entity.save()
    except ValueError as e:
        return e.message, 400
    return clean_response(entity.to_dict()), 200


def delete_entity(model, entity_id):
    if not issubclass(model, BulbModel):
        raise BulbException('Model {} must be subclass of BulbModel!'
                            .format(model.__name__))
    check_ownership(model, entity_id)
    try:
        model.get(entity_id).delete()
    except model.DoesNotExist:
        return NoContent, 404
    return NoContent, 200

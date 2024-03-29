import copy
import dateutil
import json
import pytest
import uuid

from datetime import datetime

from bulb_api.config import HIDDEN_ATTRIBUTES
from bulb_api.models import BulbModel, User


# TODO: create generators that create valid entity examples at will


def get_id_name_from_model(model):
    assert issubclass(model, BulbModel)
    id_name = model.__name__.lower()    # TODO: change '*_id' to 'id'!!
    if id_name not in ['user', 'task']:
        id_name = model.__name__.lower()[:3]
    id_name += '_id'
    return id_name


# +---------+
# | GENERAL |
# +---------+

def test_specify_bad_model():
    pass


# +--------+
# | CREATE |
# +--------+
@pytest.mark.usefixtures('fresh_db')
class TestCreateEntity:
    @pytest.fixture(scope='function')
    def entity(self, model, dummy_entities):
        return dict(dummy_entities[model][0])

    @staticmethod
    def get_create_url_path(model_class):
        return ''.join(['/', model_class.__name__.lower(), 's'])

    def test_create_entity_ok(self, client, model, entity):
        path = self.get_create_url_path(model)
        res = client.post(path, data=json.dumps(entity))
        assert res.status_code == 201
        res_entity = json.loads(res.data)
        attrs = filter(lambda a: a not in HIDDEN_ATTRIBUTES, entity.keys())
        for attr in attrs:
            assert type(res_entity[attr]) == type(entity[attr])
            assert res_entity[attr] == entity[attr]

    def test_create_entity_missing_attrs(self, client, model, entity):
        for attr in entity.keys():
            bad_entity = dict(entity)   # make copy to fuck around with
            del bad_entity[attr]        # fuck around with it
            path = self.get_create_url_path(model)
            res = client.post(path, data=json.dumps(bad_entity))
            assert res.status_code == 400

    def test_create_entity_extra_attrs(self, client, model, entity):
        bad_entity = dict(entity)
        bad_entity['foo'] = 'yourmom'
        path = self.get_create_url_path(model)
        res = client.post(path, data=json.dumps(bad_entity))
        assert res.status_code == 400

    def test_create_entity_bad_attr_types(self, client, model, entity):
        for attr in entity.keys():
            bad_entity = dict(entity)
            bad_entity[attr] = None   # test data shouldn't have any nullables
            path = self.get_create_url_path(model)
            res = client.post(path, data=json.dumps(bad_entity))
            assert res.status_code == 400

    def test_create_entity_already_exists(self, client, model, entity):
        # TODO: implement this safety check in the actual code
        path = self.get_create_url_path(model)
        res = client.post(path, data=json.dumps(entity))
        assert res.status_code == 201
        res = client.post(path, data=json.dumps(entity))
        # assert res.status_code == 409

    def test_create_entity_read_back(self, client, model, entity):
        if model is User:
            pytest.skip('Auth\'d user can\'t read info of new user.')
        path = self.get_create_url_path(model)
        res = client.post(path, data=json.dumps(entity))
        assert res.status_code == 201
        id_name = get_id_name_from_model(model)
        entity_id = json.loads(res.data)[id_name]
        entity_id_is_valid = True
        try:
            uuid.UUID(entity_id, version=4)
        except ValueError:
            pytest.fail('entity_id is not valid UUID!')
        res = client.get('/'.join([path, entity_id]))
        assert res.status_code == 200
        res_data = json.loads(res.data)
        attrs = filter(lambda a: a not in HIDDEN_ATTRIBUTES, entity.keys())
        for attr in attrs:
            assert res_data[attr] is not None
            assert res_data[attr] == entity[attr]

    def test_create_entity_with_hash_key_in_body(self, client, model, entity):
        entity[model().get_hash_key_name()] = str(uuid.uuid4())
        path = self.get_create_url_path(model)
        res = client.post(path, data=json.dumps(entity))
        assert res.status_code == 400

    def test_create_datetime_ok(self, client, model, entity):
        path = self.get_create_url_path(model)
        t0  = datetime.utcnow()
        res = client.post(path, data=json.dumps(entity))
        t1  = datetime.utcnow()
        assert res.status_code == 201
        data = json.loads(res.data)
        t_create = dateutil.parser.parse(data['create_datetime'])
        t_create = t_create.replace(tzinfo=None)
        assert t1 > t_create > t0


# +------+
# | READ |
# +------+
@pytest.mark.usefixtures('prepop_db')
class TestReadEntity:
    @staticmethod
    def get_get_url_path(model_class, e_id):
        return ''.join(['/', model_class.__name__.lower(), 's', '/', e_id])

    @staticmethod
    def get_list_url_path(model_class):
        return ''.join(['/', model_class.__name__.lower(), 's'])

    def test_get_entity_ok(self, client, model, entities, entity_ids):
        for entity, entity_id in zip(entities[model], entity_ids[model]):
            path = self.get_get_url_path(model, entity_id)
            res = client.get(path)
            assert res.status_code == 200
            res_entity = json.loads(res.data)
            assert res_entity[model().get_hash_key_name()] == entity_id
            attrs = filter(lambda a: a not in HIDDEN_ATTRIBUTES, entity.keys())
            for attr in attrs:
                assert type(res_entity[attr]) == type(entity[attr])
                assert res_entity[attr] == entity[attr]

    def test_get_entity_not_found(self, client, model):
        bad_id = str(uuid.uuid4())
        path = self.get_get_url_path(model, bad_id)
        res = client.get(path)
        assert res.status_code == 404

    def test_list_entity_ok(self, client, model, entities):
        path = self.get_list_url_path(model)
        res = client.get(path)
        assert res.status_code == 200
        res_entities = json.loads(res.data)
        assert type(res_entities) == list
        res_entities = sorted(res_entities)
        exp_entities = sorted(entities[model])
        for res_entity, entity in zip(res_entities, exp_entities):
            attrs = filter(lambda a: a not in HIDDEN_ATTRIBUTES, entity.keys())
            for attr in attrs:
                assert type(res_entity[attr]) == type(entity[attr])
                assert res_entity[attr] == entity[attr]

    def test_list_entity_paginated(self, client, model):
        path = self.get_list_url_path(model)
        q_strs = {'offset': 0}
        res = client.get(path, query_string=q_strs)
        assert res.status_code == 200
        full_len = len(json.loads(res.data))
        q_strs = {'offset': full_len}   # offset is one past end of list.
        res = client.get(path, query_string=q_strs)
        assert res.status_code == 200
        res_entities = json.loads(res.data)
        assert type(res_entities) == list
        assert len(res_entities) == 0
        q_strs = {'offset': 0, 'limit': 1}
        res = client.get(path, query_string=q_strs)
        assert res.status_code == 200
        res_entities = json.loads(res.data)
        assert type(res_entities) == list
        assert len(res_entities) == 1
        q_strs = {'offset': 1, 'limit': 1}
        res = client.get(path, query_string=q_strs)
        assert res.status_code == 200
        res_entities = json.loads(res.data)
        assert type(res_entities) == list
        assert len(res_entities) == (1 if model is not User else 0) # FIXME
        q_strs = {'offset': 0, 'limit': 2}
        res = client.get(path, query_string=q_strs)
        assert res.status_code == 200
        res_entities = json.loads(res.data)
        assert type(res_entities) == list
        assert len(res_entities) == (2 if model is not User else 1) # FIXME
        q_strs = {'limit': 0}   # 0 is valid limit, should return [].
        res = client.get(path, query_string=q_strs)
        assert res.status_code == 200
        res_entities = json.loads(res.data)
        assert type(res_entities) == list
        assert len(res_entities) == 0

    def test_list_entity_paginated_bad_params(self, client, model):
        path = self.get_list_url_path(model)
        q_strs = {'offset': 0}  # just to get len of entity list...
        res = client.get(path, query_string=q_strs)
        assert res.status_code == 200
        full_len = len(json.loads(res.data))
        q_strs = {'offset': full_len+1}
        res = client.get(path, query_string=q_strs)
        assert res.status_code == 400
        q_strs = {'limit': 65536+1}
        res = client.get(path, query_string=q_strs)
        assert res.status_code == 400
        q_strs = {'limit': -1}
        res = client.get(path, query_string=q_strs)
        assert res.status_code == 400
        q_strs = {'offset': -1}
        res = client.get(path, query_string=q_strs)
        assert res.status_code == 400
        q_strs = {'offset': 'foo'}
        res = client.get(path, query_string=q_strs)
        assert res.status_code == 400
        q_strs = {'limit': 'foo'}
        res = client.get(path, query_string=q_strs)
        assert res.status_code == 400


# +--------+
# | UPDATE |
# +--------+
@pytest.mark.usefixtures('prepop_db')
class TestUpdateEntity:
    @staticmethod
    def get_update_url_path(model_class, e_id):
        return ''.join(['/', model_class.__name__.lower(), 's', '/', e_id])

    def test_update_entity_ok(self, client, model, entities, entity_ids):
        expected, entity_id = entities[model][0], entity_ids[model][0]
        if len(entities[model]) > 1:    # TODO: explain this ish.
            new = entities[model][1]
        else:
            new = copy.deepcopy(expected)
        if 'org_id' in new.keys():  # updating this triggers 400, so don't
            del new['org_id']       # exercise it here, do so elsewhere.
        path = self.get_update_url_path(model, entity_id)
        for attr, val in new.iteritems():
            data = json.dumps({attr: val})
            res = client.put(path, data=data)
            assert res.status_code == 200
            expected[attr] = val
            updated = json.loads(res.data)
            attrs = filter(lambda a: a not in HIDDEN_ATTRIBUTES, expected.keys())
            for attr in attrs:
                assert expected[attr] == updated[attr]

    def test_update_entity_not_found(self, client, model):
        bad_id = str(uuid.uuid4())
        path = self.get_update_url_path(model, bad_id)
        res = client.put(path, data=json.dumps({}))
        assert res.status_code == 404

    def test_update_entity_bad_attr(self, client, model, entities, entity_ids):
        entity_body, entity_id = entities[model][0], entity_ids[model][0]
        bad_attr = 'mwahaha'
        entity_body[bad_attr] = 'gertcha'
        path = self.get_update_url_path(model, entity_id)
        res = client.put(path, data=json.dumps(entity_body))
        assert res.status_code == 400

    def test_update_entity_bad_attr_types(self, client, model, entities,
                                          entity_ids):
        entity, entity_id = entities[model][0], entity_ids[model][0]
        path = self.get_update_url_path(model, entity_id)
        attrs = filter(lambda a: a not in HIDDEN_ATTRIBUTES, entity.keys())
        for attr in attrs:
            fresh_body = dict(entity)
            fresh_body[attr] = None     # test data shouldn't have any nullables
            res = client.put(path, data=json.dumps(fresh_body))
            assert res.status_code == 400

    def test_update_entity_read_back(self):
        # TODO --
        # use this:
        #   attrs = filter(lambda a: a not in HIDDEN_ATTRIBUTES, entity.keys())
        pass

    def test_update_entity_id_in_body(self, client, model, entity_ids):
        entity_id = entity_ids[model][0]
        id_name = get_id_name_from_model(model)
        bad_body = {id_name: entity_id}
        path = self.get_update_url_path(model, entity_id)
        res = client.put(path, data=json.dumps(bad_body))
        assert res.status_code == 200   # we should allow this, just del ID
        worse_body = {'id': entity_id}  # should fail b/c 'id' isn't valid key
        res = client.put(path, data=json.dumps(worse_body))
        assert res.status_code == 400
        mismatch_uuid = str(uuid.uuid4())
        worst_body = {id_name: mismatch_uuid}
        res = client.put(path, data=json.dumps(worst_body))
        assert res.status_code == 400   # can't allow mismatches in IDs passed

    def test_update_entity_last_modified_datetime_ok(self):
        # TODO: implement this behavior in handlers.py! also, assert that it's
        #       greater than create_datetime.
        # --
        pass


# +--------+
# | DELETE |
# +--------+
@pytest.mark.usefixtures('prepop_db')
class TestDeleteEntity:
    @staticmethod
    def get_delete_url_path(model_class, e_id):
        return ''.join(['/', model_class.__name__.lower(), 's', '/', e_id])

    def test_delete_entity_ok(self, client, model, entity_ids):
        for entity_id in entity_ids[model]:
            path = self.get_delete_url_path(model, entity_id)
            res = client.delete(path)
            assert res.status_code == 200

    def test_delete_entity_not_found(self, client, model):
        bad_id = str(uuid.uuid4())
        path = self.get_delete_url_path(model, bad_id)
        res = client.delete(path)
        assert res.status_code == 404

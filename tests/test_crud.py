import json
import pytest
import uuid

from bulb_api.models import BulbModel


# TODO: MAKE EACH TYPE OF ACCESS ITS OWN CLASS!!
# - can then parameterize by class
# - can then have class-wide fixture usage
# - create generators that create valid entity examples at will
# - create DDB fixture, and pre-populated it!
# - parameterize all this shnit over ALL entity types


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
    @pytest.fixture(scope='function', params=BulbModel.__subclasses__())
    def model(self, request):
        return request.param

    @pytest.fixture(scope='function')
    def entity(self, model, dummy_entities):
        return dummy_entities[model][1]

    @staticmethod
    def get_create_url_path(model_class):
        return ''.join(['/', model_class.__name__.lower(), 's'])

    def test_create_entity_ok(self, client, model, entity):
        path = self.get_create_url_path(model)
        res = client.post(path, data=json.dumps(entity),
                                content_type='application/json')
        assert res.status_code == 201

    def test_create_entity_missing_attrs(self, client, model, entity):
        for attr in entity.keys():
            bad_entity = dict(entity)   # make copy to fuck around with
            del bad_entity[attr]        # fuck around with it
            path = self.get_create_url_path(model)
            res = client.post(path, data=json.dumps(bad_entity),
                                    content_type='application/json')
            print attr
            assert res.status_code == 400

    def test_create_entity_extra_attrs(self, client, model, entity):
        bad_entity = dict(entity)
        bad_entity['foo'] = 'yourmom'
        path = self.get_create_url_path(model)
        res = client.post(path, data=json.dumps(bad_entity),
                                content_type='application/json')
        assert res.status_code == 400

    def test_create_entity_bad_attr_types(self, client, model, entity):
        for attr in entity.keys():
            bad_entity = dict(entity)
            bad_entity[attr] = None   # test data shouldn't have any nullables
            path = self.get_create_url_path(model)
            res = client.post(path, data=json.dumps(bad_entity),
                                    content_type='application/json')
            assert res.status_code == 400

    def test_create_entity_already_exists(self, client, model, entity):
        # TODO: implement this safety check in the actual code
        path = self.get_create_url_path(model)
        res = client.post(path, data=json.dumps(entity),
                                content_type='application/json')
        # assert res.status_code == 201
        res = client.post(path, data=json.dumps(entity),
                                content_type='application/json')
        # assert res.status_code == 409

    def test_read_newly_created(self, client, model, entity):
        path = self.get_create_url_path(model)
        res = client.post(path, data=json.dumps(entity),
                                    content_type='application/json')
        assert res.status_code == 201
        id_name = model.__name__.lower()    # TODO: change '*_id' to 'id'!!
        if not id_name == 'user':
            id_name = model.__name__.lower()[:3]
        id_name += '_id'
        entity_id = json.loads(res.data)[id_name]
        entity_id_is_valid = True
        try:
            uuid.UUID(entity_id, version=4)
        except ValueError:
            entity_id_is_valid = False
        assert entity_id_is_valid
        res = client.get('/'.join([path, entity_id]))
        assert res.status_code == 200
        res_data = json.loads(res.data)
        for attr in entity.keys():
            assert res_data[attr]
            assert res_data[attr] == entity[attr]


# +------+
# | READ |
# +------+

def test_get_entity_ok():
    pass


def test_get_entity_not_found():
    pass


def test_list_entity_ok():
    pass


# +--------+
# | UPDATE |
# +--------+

def test_update_entity_ok():
    pass


def test_update_entity_missing_attrs():
    pass


def test_update_entity_extra_attrs():
    pass


def test_update_entity_bad_attr_types():
    pass


# +--------+
# | DELETE |
# +--------+

def test_delete_entity_ok():
    pass


def test_delete_entity_not_found():
    pass

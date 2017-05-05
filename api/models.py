import os
import uuid

from pynamodb.attributes import (
        UnicodeAttribute,
        ListAttribute,
        NumberAttribute,
        UTCDateTimeAttribute
)
from pynamodb.exceptions import GetError
from pynamodb.models import Model


class BulbModel(Model):
    # def __repr__(self):   # TODO
    # TODO: make this an abstract class

    class Meta:
        host = None
        if os.environ.get('FLASK_DEBUG'):
            host = 'http://localhost:8000'
        read_capacity_units = 1
        write_capacity_units = 1

    def get_hash_key_name(self):
        """ Get the name of this item's hash_key attribute. """
        return self._hash_key_attribute().attr_name

    # TODO add custom serializer that snags all @properties / Model.*Attribute
    @classmethod
    def get_unused_uuid(cls):
        max_tries = 3
        for _ in range(max_tries):
            candidate = str(uuid.uuid4())
            try:
                cls.get(candidate)
                print '{}: ID {} already in use!'.format(cls.Meta.table_name,
                                                        candidate)
            except cls.DoesNotExist:
                return candidate
            except GetError:
                return candidate
        else:
            msg = 'Can\'t find unique UUID after {} tries!'.format(max_tries)
            raise Exception(msg)

    def to_dict(self):
        return dict(self.attribute_values)

    def update_from_dict(self, body):
        """ Updates the entity with the values provided in dict `body`. """
        for key, value in body.items():
            if key == self.get_hash_key_name():
                raise Exception('can\'t overwrite hash key!')
            elif key not in self.attribute_values.keys() \
                    and key not in self._attributes.keys():
                raise Exception('key must be a valid attribute!')
            else:
                setattr(self, key, value)


class Document(BulbModel):
    class Meta(BulbModel.Meta):
        table_name = 'Document'

    doc_id = UnicodeAttribute(hash_key=True)
    create_datetime = UTCDateTimeAttribute()
    organization = UnicodeAttribute()
    uri = UnicodeAttribute()
    due_date = UTCDateTimeAttribute(null=True)
    progress = NumberAttribute(null=True)
    status = UnicodeAttribute()
    name = UnicodeAttribute()
    type = UnicodeAttribute(null=True)
    note = UnicodeAttribute(null=True)


class Organization(BulbModel):
    class Meta(BulbModel.Meta):
        table_name = 'Organization'

    org_id = UnicodeAttribute(hash_key=True)
    create_datetime = UTCDateTimeAttribute()
    type = UnicodeAttribute()
    name = UnicodeAttribute()
    users = ListAttribute()


class Resource(BulbModel):
    class Meta(BulbModel.Meta):
        table_name = 'Resource'

    res_id = UnicodeAttribute(hash_key=True)
    create_datetime = UTCDateTimeAttribute()
    name = UnicodeAttribute()
    url = UnicodeAttribute()
    mailto_uri = UnicodeAttribute(null=True)
    s3_thumbnail_uri = UnicodeAttribute(null=True)


class User(BulbModel):
    """
    LSI might be good here over GSI, but at the moment, we haven't a need for a
    range_key, a hard requisite for LSI's. So, we'll go with a GSI indexed on
    email. Should consider moving to LSI when have range key, as it doesn't
    require additional thpt provisioning like GSI's do.
    """
    class Meta(BulbModel.Meta):
        # TODO index this shnit by email
        table_name = 'User'

    user_id = UnicodeAttribute(hash_key=True)
    email = UnicodeAttribute()
    create_datetime = UTCDateTimeAttribute()
    organizations = ListAttribute()
    name = UnicodeAttribute()

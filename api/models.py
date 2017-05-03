from uuid import UUID, uuid4
from datetime import datetime
from pynamodb.models import Model
from pynamodb.attributes import (
        Attribute, UnicodeAttribute, ListAttribute, NumberAttribute, UTCDateTimeAttribute
)

class BulbModel(Model):
    # def __repr__(self):
        # TODO

    def get_hash_key_name(self):
        """ Get the name of this item's hash_key attribute. """
        # TODO: make this an abstract method?
        return self._hash_key_attribute().attr_name

    # TODO add custom serializer that snags all @properties / Model.*Attribute
    @staticmethod   # gonna need to remove so the method can actually check...
    def get_unused_uuid():
        candidate = str(uuid4())
        # TODO verify that this UUID isn't already in the table
        return candidate

    def to_dict(self):
        return dict(self.attribute_values)

    def update_from_dict(self, d):
        """ Updates the entity with the values provided in dict `body`. """
        for key, value in d.items():
            print key, value
            if key == self.get_hash_key_name():
                raise Exception('can\'t overwrite hash key!')
            elif key not in self.attribute_values.keys():
                raise Exception('key must be valid attribute!')
            else:
                setattr(self, key, value)


class Document(BulbModel):
    class Meta:
        table_name = 'Document'

    doc_id = UnicodeAttribute(hash_key=True)
    create_datetime = UTCDateTimeAttribute()
    organization = UnicodeAttribute()
    uri = UnicodeAttribute()
    due_date = UTCDateTimeAttribute()
    progress = NumberAttribute()
    status = UnicodeAttribute()
    name = UnicodeAttribute()
    type = UnicodeAttribute()
    note = UnicodeAttribute()


class Organization(BulbModel):
    class Meta:
        table_name = 'Organization'

    org_id = UnicodeAttribute(hash_key=True)
    create_datetime = UTCDateTimeAttribute()
    type = UnicodeAttribute()
    name = UnicodeAttribute()
    users = ListAttribute()


class Resource(BulbModel):
    class Meta:
        table_name = 'Resource'

    res_id = UnicodeAttribute(hash_key=True)
    create_datetime = UTCDateTimeAttribute()
    name = UnicodeAttribute()
    url = UnicodeAttribute()
    mailto_uri = UnicodeAttribute()
    s3_thumbnail_uri = UnicodeAttribute()


class User(BulbModel):
    """
    LSI might be good here over GSI, but at the moment, we haven't a need for a
    range_key, a hard requisite for LSI's. So, we'll go with a GSI indexed on
    email. Should consider moving to LSI when have range key, as it doesn't
    require additional thpt provisioning like GSI's do.
    """
    class Meta:
        # TODO index this shnit by email
        table_name = 'User'
        # TODO v-- move all below to BulbModel
        host = 'http://localhost:8000'
        read_capacity_units = 1
        write_capacity_units = 1

    user_id = UnicodeAttribute(hash_key=True)
    email = UnicodeAttribute()
    create_datetime = UTCDateTimeAttribute()
    organizations = ListAttribute()
    name = UnicodeAttribute()



import os
import re
import uuid

from pynamodb.attributes import (
        UnicodeAttribute,
        ListAttribute,
        NumberAttribute,
        UTCDateTimeAttribute
)
from pynamodb.exceptions import GetError
from pynamodb.models import Model

from .exceptions import BulbException
from .indexes import (
    EmailIndexForUser,
    OrgIndexForDocument,
    OrgIndexForResource,
    OrgIndexForTask,
    OrgIndexForUser,
)


class BulbModel(Model):
    # def __repr__(self):   # TODO
    # TODO: make this an abstract class

    class Meta:
        host = None     # if this stays None, we'll use prod DDB
        if os.environ.get('FLASK_DEBUG'):
            # try to grab + clean URL for ddb_local container if it's --link'd
            host = os.environ.get('DDB_LOCAL_PORT', 'http://localhost:8000')
            host = re.sub('tcp', 'http', host)
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
            except (cls.DoesNotExist, GetError):
                return candidate
        else:
            msg = 'Can\'t find unique UUID after {} tries!'.format(max_tries)
            raise BulbException(msg)

    def to_dict(self):
        return dict(self.attribute_values)

    def update_from_dict(self, body):
        """ Updates the entity with the values provided in dict `body`. """
        for key, value in body.items():
            if key == self.get_hash_key_name():
                raise BulbException('cant overwrite hash key `{}`'.format(key))
            elif key not in self.attribute_values.keys() \
                    and key not in self._attributes.keys():
                raise BulbException('key `{}` must be valid attr'.format(key))
            elif key is not None and value is not None:     # TODO: write a
                setattr(self, key, value)                   # test around this.


class Document(BulbModel):
    class Meta(BulbModel.Meta):
        table_name = 'Document'

    doc_id = UnicodeAttribute(hash_key=True)
    org_id = UnicodeAttribute()
    create_datetime = UTCDateTimeAttribute()
    uri = UnicodeAttribute()
    due_date = UTCDateTimeAttribute(null=True)
    progress = NumberAttribute(null=True)
    status = UnicodeAttribute()
    name = UnicodeAttribute()
    type = UnicodeAttribute(null=True)
    note = UnicodeAttribute(null=True)

    org_index = OrgIndexForDocument()


class Organization(BulbModel):
    class Meta(BulbModel.Meta):
        table_name = 'Organization'

    org_id = UnicodeAttribute(hash_key=True)
    create_datetime = UTCDateTimeAttribute()
    type = UnicodeAttribute(null=True)
    name = UnicodeAttribute(null=True)  # TODO: require this, make input field
    users = ListAttribute()


class Resource(BulbModel):
    class Meta(BulbModel.Meta):
        table_name = 'Resource'

    res_id = UnicodeAttribute(hash_key=True)
    org_id = UnicodeAttribute()
    create_datetime = UTCDateTimeAttribute()
    name = UnicodeAttribute()
    url = UnicodeAttribute()
    mailto_uri = UnicodeAttribute(null=True)
    s3_thumbnail_uri = UnicodeAttribute(null=True)

    org_index = OrgIndexForResource()


class User(BulbModel):
    """
    LSI might be good here over GSI, but at the moment, we haven't a need for a
    range_key, a hard requisite for LSI's. So, we'll go with a GSI indexed on
    email. Should consider moving to LSI when have range key, as it doesn't
    require additional thpt provisioning like GSI's do.
    """
    class Meta(BulbModel.Meta):
        table_name = 'User'

    user_id = UnicodeAttribute(hash_key=True)
    org_id = UnicodeAttribute(null=True)    # strictly for user creation.
    email = UnicodeAttribute()
    password_hash = UnicodeAttribute()
    create_datetime = UTCDateTimeAttribute()
    name = UnicodeAttribute()

    email_index = EmailIndexForUser()
    org_index = OrgIndexForUser()


class Task(BulbModel):
    class Meta(BulbModel.Meta):
        table_name = 'Task'

    task_id = UnicodeAttribute(hash_key=True)
    org_id = UnicodeAttribute()
    create_datetime = UTCDateTimeAttribute()
    name = UnicodeAttribute()
    url = UnicodeAttribute(null=True)
    workspaces = ListAttribute()
    priority = NumberAttribute()
    status = UnicodeAttribute()

    org_index = OrgIndexForTask()

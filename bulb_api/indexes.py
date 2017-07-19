from pynamodb.attributes import (
        UnicodeAttribute,
)
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection


class EmailIndexForUser(GlobalSecondaryIndex):
    """ TODO
    """
    class Meta:
        index_name = 'email-index'
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    email = UnicodeAttribute(hash_key=True)


class OrgIndexForDocument(GlobalSecondaryIndex):
    """ TODO
    """
    class Meta:
        index_name = 'org-index'
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    org_id = UnicodeAttribute(hash_key=True)


class OrgIndexForResource(GlobalSecondaryIndex):
    """ TODO
    """
    class Meta:
        index_name = 'org-index'
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    org_id = UnicodeAttribute(hash_key=True)


class OrgIndexForTask(GlobalSecondaryIndex):
    """ TODO
    """
    class Meta:
        index_name = 'org-index'
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    org_id = UnicodeAttribute(hash_key=True)


class OrgIndexForUser(GlobalSecondaryIndex):
    """ TODO
    """
    class Meta:
        index_name = 'org-index'
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    org_id = UnicodeAttribute(hash_key=True)

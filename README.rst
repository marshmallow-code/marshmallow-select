******************
marshmallow-select
******************

Declare Model.query
===================

.. code-block:: python
    class BaseModel(object):
        @classmethod
        def query(cls):
            return session.query(cls)


    Base = declarative_base(cls=BaseModel)


Add the mixin
=============

.. code-block:: python
    from marshmallow_select import SchemaQueryMixin


    class BaseModel(SchemaQueryMixin, object):
        ...


Query with schemas
==================

.. code-block:: python
    from schemas import UserSchema
    from models import User

    qry = User.schema_query(UserSchema)


    class ShortUserSchema(UserSchema):
        class Meta:
            fields = ['id', 'name']


    # fetches only name and id
    short_qry = User.schema_query(ShortUserSchema)
    
    # fetches everything, but in one single joined query, even if
    # fields of User (or fields of fields of user) are lazily-loaded
    joined_qry = User.schema_query(UserSchema, unlazify=True)

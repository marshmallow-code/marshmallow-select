******************
marshmallow-select
******************

Declare Model._base_query
===================

.. code-block:: python

    class BaseModel(object):
        @classmethod
        def _base_query(cls):
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


TODO
====

0. Make default :code:`_base_query` if some sensible way of
   discovering the session is available (e.g. user can register the
   scoped_session obj or some other method of getting the current
   session)

1. Some simple way of detecting & reporting if the schema "covers" the
   query (i.e. serializing with the schema will not produce additional
   queries)

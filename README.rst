******************
marshmallow-select
******************

Use marshmallow schemas to generate select clauses for sqlalchemy
queries.


Usage
=====

.. code-block:: python

    from marshmallow_select import SchemaFilter

    from schemas import UserSchema
    from models import User

    qry = User.some_query_method()


    class ShortUserSchema(UserSchema):
        class Meta:
            fields = ['id', 'name']


    # fetches only name and id
    sf = SchemaFilter(ShortUserSchema())
    short_qry = sf(qry)
    
    # fetches everything, but in one single joined query, even if
    # fields of User (or fields of fields of user) are lazily-loaded
    sf = SchemaFilter(UserSchema(), unlazify=True)
    joined_qry = sf(qry)


You can also filter nested fields

.. code-block:: python

    from marshmallow_select import SchemaFilter

    from schemas import UserSchema, OrganizationSchema
    from models import User

    qry = User.some_query_method()


    class ShortOrganizationSchema(OrganizationSchema):
        class Meta:
            fields = ['id', 'name']


    class UserWithShortOrgSchema(UserSchema):
        organization = Nested(ShortOrganizationSchema)


    # Will join-load the user's org, but only fetch id & name
    sf = SchemaFilter(UserWithShortOrgSchema())
    new_qry = sf(qry)


Tips
====

marshmallow-select makes reasonable efforts to detect fields that are
not directly on the schema. For example, if you have a model with a
field :code:`approved` and a schema like

.. code-block:: python

    class FooSchema(Schema):
        is_approved = Boolean(attribute="approved")

marshmallow-select will include :code:`approved` in the list of fields
it will fetch. Nonetheless, there is nothing realistic it can do about
the following case

.. code-block:: python

    class User(BaseModel):
        first_name = Column(String(100))
        last_name  = Column(String(100))

        @property
        def full_name(self):
            return ' '.join([self.first_name, self.last_name])


    class UserSchema(Schema):
        full_name = String()


The solution in this case (aside from telling you to do less of that;
we all have legacy code) is to explicitly bring these fields to the
attention of marshmallow-select without actually adding them to the
list of output fields

.. code-block:: python
    class UserSchema(Schema):
        full_name = String()
        first_name = Field(load_only=True)
        last_name = Field(load_only=True)

since marshmallow-select treats any fields on the schema as fields
that should be fetched, even if the schema declares that they will not
actually be serialized (if your existing schema has load_only fields
you want marshmallow-select to not fetch, you should :code:`exclude`
them).

Notes
=====

This code is semantically versioned. Just because it says "1.0.0"
doesn't mean it's even vaguely production-ready.

TODO
====

0. Performance improvements: I never really bothered to cache some of
   the more expensive introspections. It runs on order of tens of
   milliseconds, but can push up to hundreds (when in fact it should
   probably be on the order of microseconds). This is fine when you're
   optimizing a query that should be immediate but is taking minutes
   because of k*n+1 query bugs, but can sometimes mean the difference
   between whether you can get a query down to sub-second or not.

   It should also be possible to perform the necessary introspections
   at application boot time, instead of query execution time. This is
   in-principle possible, although would require losing some
   flexibility.

1. Some simple way of detecting & reporting if the schema "covers" the
   query (i.e. serializing with the schema will not produce additional
   queries). Currently I just turn on sqlalchemy engine echoing and
   run the query and the serialization in the console and see if any
   extra queries happen.

2. Support for multi-entity queries (e.g. explicit joins of 2 models
   without existing relationships). This rarely comes up for us (most
   of our queries which involve explicit joins are aggregations), but
   might be useful to someone.

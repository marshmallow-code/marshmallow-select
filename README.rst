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


Notes
=====

This code is semantically versioned. Just because it says "1.0.0"
doesn't mean it's even vaguely production-ready.

TODO
====

0. Some simple way of detecting & reporting if the schema "covers" the
   query (i.e. serializing with the schema will not produce additional
   queries)

1. unlazify doesn't appear to work 100% of the time; figure out why
   (think I fixed this).

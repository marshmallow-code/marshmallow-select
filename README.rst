******************
marshmallow-select
******************

Use marshmallow schemas to generate select clauses for sqlalchemy
queries.

Installation
============

:code:`pip install marshmallow-select`. Or see the
`guide to pip installing from github repos.`__

.. __: https://pip.pypa.io/en/stable/reference/pip_install/#vcs-support

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

Schema fields which do not map to model fields
----------------------------------------------

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

Separately-added values
-----------------------

Sometimes when trying to integrate schemas into legacy code, you end
up with particular fields which are added separately from normal
serialization-via-schema. In other words something like:


.. code-block:: python

    # used by api resource A
    def fetch_foos():
        foos = read_foos_from_db()
        return {'foos_list': [FooSchema().dump(foo) for foo in foos]}


    # used by api resource B
    def fetch_foos_special_case():
        foos = read_foos_from_db()
        dumped_foos = [FooSchema().dump(foo) for foo in foos]
        for foo in dumped_foos:
            foo['special_case_field'] = get_special_value()
        return {'special_foos_list': dumped_foos}

Perhaps in addition to using schemas for serialization, you also wish
to use them to generate swagger/apispec markup. In this situation,
marshmallow-select is perfectly happy with you doing something like:

.. code-block:: python

    class SpecialFooSchema(FooSchema):
        # or whatever type get_special_value returns.
        special_case_field = Integer()


    # This schema could be used both to serialize both cases of Foo
    # objects, and to filter queries for them.
    class DualPurposeSpecialFooSchema(FooSchema):
        special_case_field = Integer(missing=None)

In other words, the marshmallow-select does not care if a field cannot
be found. Filtering via either of the above schema when querying for
Foo objects should be equivalent to querying with the parent schema.

Notes
=====

This code is semantically versioned. Just because it says "1.0.0"
doesn't mean it's even vaguely production-ready. The fact that I'm
using it in production doesn't mean you should.

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

3. Would be nice to have some kind of metaclass mixin so that instead
   of declaring dependent fields (like :code:`first_name`) load_only,
   they could just be listed in the metaclass in a tuple called
   :code:`dependent_fields` or something.

Acknowledgements
================

Originally written on behalf of Distribute_

.. _Distribute: //distribute.com

.. image:: dtd_emblem.png
    :align: center
    :alt: distribute logo

You should totally check them out if you're in the wholesale
purchasing|distribution space.


LICENSE
=======

marshmallow-select is distributed under the terms of the WTFPL,
version 2. See COPYING_.

.. _COPYING: https://github.com/marshmallow-code/marshmallow-select/blob/master/COPYING


WARRANTY
========

Users who believe that it's my fault if something that goes wrong with
their software as a result of using this code should consult the case
of *Arkell v. Pressdram*.


See Also
========

My blog post_ announcing the package. Further announcements (there'll
probably be at least one) will be tagged marshmallow-select_.

.. _post: https://dradetsky.github.io/marshmallow-select.html

.. _marshmallow-select: https://dradetsky.github.io/tags/marshmallow-select.html

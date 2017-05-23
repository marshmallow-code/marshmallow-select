from marshmallow.fields import (
    List,
    Nested
)
from sqlalchemy.orm import (
    joinedload,
    defaultload,
    noload,
    load_only,
    class_mapper
)


class SchemaProjectionGenerator(object):
    def __init__(self, schema_inst, query_cls, filter_only_these=None):
        self.schema = schema_inst
        self.cls = query_cls
        self.mapper = class_mapper(query_cls)
        self.filter_only_these = filter_only_these

    @property
    def config(self):
        cfg = {
            'reload': self.reload_field_names,
            'load_only': self.load_only_field_names,
            'noload': self.noload_link_field_names,
            'childs': self.recurse_on_link_fields()
        }
        return cfg

    def recurse_on_link_fields(self):
        name_recursion_pairs = [(name, self.recurse_on_name(name))
                                for name in self.link_field_names]
        filtered_pairs = [(name, rec) for name, rec in name_recursion_pairs if rec]
        ret = dict(filtered_pairs)
        return ret

    def recurse_on_name(self, name):
        cls = self.__class__
        next_schema = get_next_schema(self.schema, name)
        next_class = get_next_class(self.mapper, name)
        if next_schema is None or next_class is None:
            return None
        else:
            return cls(next_schema(), next_class).config

    @property
    def reload_field_names(self):
        names = (self.class_link_field_names - self.noload_link_field_names)
        return names

    @property
    def nonlink_field_names(self):
        names = (self.class_nonlink_field_names & self.schema_field_names)
        return names

    @property
    def noload_link_field_names(self):
        names = self.basic_noload_link_field_names | self.renamed_attr_link_fields
        return names

    @property
    def basic_noload_link_field_names(self):
        names = (self.class_link_field_names - self.schema_field_names)
        return names

    @property
    def load_only_field_names(self):
        names = self.nonlink_field_names | self.renamed_attr_nonlink_fields
        return names

    @property
    def link_field_names(self):
        names = (self.schema_field_names & self.class_link_field_names)
        if self.filter_only_these:
            names = {n for n in names if n in self.filter_only_these}
        return names

    @property
    def class_link_field_names(self):
        class_names = set(self.mapper.relationships.keys())
        return class_names

    @property
    def class_nonlink_field_names(self):
        class_names = set(self.mapper.column_attrs.keys())
        return class_names

    @property
    def schema_field_names(self):
        return set(self.schema.fields.keys())

    @property
    def unaccounted_for_field_names(self):
        """
        Most field names are either the names of direct fields or link
        fields. There are some other cases which require special
        processing,
        """
        names = ((self.schema_field_names - self.class_nonlink_field_names) -
                 self.class_link_field_names)
        return names

    @property
    def renamed_attr_link_fields(self):
        names = [name for field_type, name in self.find_renamed_attr_fields()
                 if field_type == 'link']
        return set(names)

    @property
    def renamed_attr_nonlink_fields(self):
        names = [name for field_type, name in self.find_renamed_attr_fields()
                 if field_type == 'nonlink']
        return set(names)

    def find_renamed_attr_fields(self):
        result = [self.check_for_renamed_attr(name) for name
                  in self.unaccounted_for_field_names]
        renamed_fields = [(field_type, name) for field_type, name in result if name]
        return renamed_fields

    def check_for_renamed_attr(self, name):
        schema_field = self.schema.fields[name]
        field_attr = schema_field.attribute
        # If there is no attr set in the schema class, this field is
        # set to None
        if not field_attr:
            return False, None
        elif field_attr in self.class_link_field_names:
            return 'link', field_attr
        elif field_attr in self.class_nonlink_field_names:
            return 'nonlink', field_attr
        else:
            return False, None


def get_next_schema(schema, name):
    field = schema.fields[name]
    if type(field) is List and type(field.container) is not Nested:
        return None
    elif type(field) is List:
        return field.container.nested
    elif type(field) is Nested:
        return field.nested
    else:
        return None


def get_next_class(mapper, name):
    return mapper.relationships[name].mapper.class_


def project_query(qry, cfg, opt_prefix=None, loader=defaultload):
    """
    BFSs through config tree modifying query

    opt_prefix is a path from the root of up to the child we are about
    to modify.
    """
    def add_to_opt_prefix(old_prefix, new_name):
        if old_prefix:
            new_prefix = getattr(old_prefix, loader.__name__)(new_name)
        else:
            new_prefix = loader(new_name)
        return new_prefix

    def project_current_depth(qry, cfg, opt_prefix):
        load_only_opt = cfg['load_only']
        noload_opt = cfg['noload']
        reload_opt = cfg['reload']

        if opt_prefix:
            qry = qry.options(opt_prefix.load_only(*load_only_opt))
        else:
            qry = qry.options(load_only(*load_only_opt))

        for name in noload_opt:
            if opt_prefix:
                qry = qry.options(opt_prefix.noload(name))
            else:
                qry = qry.options(noload(name))

        for name in reload_opt:
            reload_expr = add_to_opt_prefix(opt_prefix, name)
            qry = qry.options(reload_expr)

        return qry

    projected_qry = qry

    for name, child_cfg in cfg['childs'].items():
        child_opt_prefix = add_to_opt_prefix(opt_prefix, name)
        projected_qry = project_query(projected_qry,
                                      child_cfg,
                                      child_opt_prefix)

    projected_qry = project_current_depth(projected_qry, cfg, opt_prefix)
    return projected_qry


class SchemaFilter(object):
    def __init__(self, schema, unlazify=False):
        if isinstance(schema, type):
            self.schema_inst = schema()
        else:
            self.schema_inst = schema

        if unlazify:
            self.loader = joinedload
        else:
            self.loader = defaultload

    def __call__(self, qry, cls=None):
        if not cls:
            cls = qry._entity_zero().class_

        projector = SchemaProjectionGenerator(self.schema_inst, cls)
        projection_cfg = projector.config

        new_qry = project_query(qry, projection_cfg, loader=self.loader)
        return new_qry

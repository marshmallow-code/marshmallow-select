from marshmallow.fields import (
    List,
    Nested
)
from sqlalchemy.orm import class_mapper


class SchemaProjectionGenerator(object):
    def __init__(self, schema_inst, query_cls, filter_only_these=None):
        self.schema = schema_inst
        self.cls = query_cls
        self.mapper = class_mapper(query_cls)
        self.filter_only_these = filter_only_these

    @property
    def config(self):
        cfg = {
            'load_only': self.nonlink_field_names,
            'noload': self.noload_link_field_names,
            'childs': self.recurse_on_link_fields()
        }
        return cfg

    def recurse_on_link_fields(self):
        ret = {name: self.recurse_on_name(name) for name in self.link_field_names}
        return ret

    def recurse_on_name(self, name):
        cls = self.__class__
        next_schema = get_next_schema(self.schema, name)
        next_class = get_next_class(self.mapper, name)
        return cls(next_schema(), next_class).config

    @property
    def nonlink_field_names(self):
        names = (self.class_nonlink_field_names & self.schema_field_names)
        return names

    @property
    def noload_link_field_names(self):
        names = (self.class_link_field_names - self.schema_field_names)
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


def get_next_schema(schema, name):
    field = schema.fields[name]
    if type(field) is List:
        return field.container.nested
    elif type(field) is Nested:
        return field.nested
    else:
        raise ValueError('zomg')


def get_next_class(mapper, name):
    return mapper.relationships[name].mapper.class_


def project_query(qry, cfg, opt_prefix=None, loader=defaultload):
    def add_to_opt_prefix(old_prefix, new_name):
        if old_prefix:
            new_prefix = getattr(old_prefix, loader.__name__)(new_name)
        else:
            new_prefix = loader(new_name)
        return new_prefix

    def project_current_depth(qry, cfg, opt_prefix):
        load_only_opt = cfg['load_only']
        noload_opt = cfg['noload']

        if opt_prefix:
            qry = qry.options(opt_prefix.load_only(*load_only_opt))
        else:
            qry = qry.options(load_only(*load_only_opt))

        for name in noload_opt:
            if opt_prefix:
                qry = qry.options(opt_prefix.noload(name))
            else:
                qry = qry.options(noload(name))

        return qry

    projected_qry = qry

    for name, child_cfg in cfg['childs'].items():
        child_opt_prefix = add_to_opt_prefix(opt_prefix, name)
        projected_qry = project_query(projected_qry,
                                      child_cfg,
                                      child_opt_prefix)

    projected_qry = project_current_depth(projected_qry, cfg, opt_prefix)
    return projected_qry

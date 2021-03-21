import os
import importlib
import yaml

from collections import namedtuple, abc

from .errors import InputError
from .tools import custom_eval

def listify(obj):
    listified = False
    if not isinstance(obj, list):
        obj = [obj]
        listified = True
    return obj, listified

def unlistify(obj, listified):
    if listified:
        assert len(obj) == 1
        obj = obj[0]
    return obj


class NamedObjects(abc.MutableMapping):
    """Class to track named objects and their descriptions"""
    def __init__(self, global_dct):
        names, dcts = self.all_name_descriptions(global_dct)
        self.objects = {name: None for name in names}
        self.descriptions = {name: dct for name, dct in zip(names, dcts)}

    def __getitem__(self, key):
        return self.objects[key]

    def __setitem__(self, key, value):
        self.objects[key] = value

    def __delitem__(self, key):
        del self.objects[key]

    def __iter__(self):
        return iter(self.objects)

    def __len__(self):
        return len(self.objects)

    @staticmethod
    def all_name_descriptions(dct):
        """Find all the named objets and their dict descriptions

        Parameters
        ----------
        dct : dict
            output from loading YAML
        """
        names = []
        dcts = []
        name = None
        if isinstance(dct, list):
            for item in dct:
                name_list, dct_list = \
                        NamedObjects.all_name_descriptions(item)
                names.extend(name_list)
                dcts.extend(dct_list)
        elif isinstance(dct, dict):
            for k, v in dct.items():
                if isinstance(v, (dict, list)):
                    name_list, dct_list = \
                            NamedObjects.all_name_descriptions(v)
                    names.extend(name_list)
                    dcts.extend(dct_list)
            try:
                name = dct['name']
            except KeyError:
                pass
            else:
                names.append(name)
                dcts.append(dct)

        return names, dcts


class InstanceBuilder:
    # TODO: add schema as an input so we can autogenerate our JSON schema!
    def __init__(self, builder, attribute_table, defaults=None, module=None,
                 remapper=None):
        self.module = module
        self.builder = builder
        self.attribute_table = attribute_table
        # TODO use none_to_default
        if remapper is None:
             remapper = lambda x: x
        self.remapper = remapper
        if defaults is None:
            defaults = {}
        self.defaults = defaults

    def select_builder(self, dct):
        if self.module is not None:
            builder = getattr(importlib.import_module(self.module), self.builder)
        else:
            builder = self.builder
        return builder


    def __call__(self, dct):
        # TODO: support aliases in dct[attr]
        input_dct = self.defaults.copy().update(dct)
        # new_dct = {attr: func(dct[attr], named_objs)
                   # for attr, func in self.attribute_table.items()}
        new_dct = {}
        for attr, func in self.attribute_table.items():
            new_dct[attr] = func(dct[attr])
        builder = self.select_builder(new_dct)
        ops_dct = self.remapper(new_dct)
        return builder(**ops_dct)


class Parser:
    """Generic parse class; instances for each category"""
    def __init__(self, type_dispatch, label):
        self.type_dispatch = type_dispatch
        self.label = label
        self.named_objs = {}

    def _parse_str(self, name):
        try:
            return self.named_objs[name]
        except KeyError as e:
            raise e  # TODO: replace with better error

    # def _parse_str(self, name, named_objs):
        # obj = named_objs[name]
        # if obj is None:
            # try:
                # definition = named_objs.definitions[name]
            # except KeyError:
                # raise InputError.unknown_name(self.label, name)
            # else:
                # obj = self(definition, named_objects)
            # named_objs[name] = obj

        # return obj

    def _parse_dict(self, dct):
        dct = dct.copy()  # make a local copy
        name = dct.pop('name', None)
        type_name = dct.pop('type')
        obj = self.type_dispatch[type_name](dct)
        # return obj.named(name)
        if name is not None:
            if name in self.named_objs:
                raise RuntimeError("Same name twice")  # TODO improve
            obj = obj.named(name)
            self.named_objs[name] = obj


    def parse(self, dct):
        if isinstance(dct, str):
            return self._parse_str(dct)
        else:
            return self._parse_dict(dct)

    def __call__(self, dct):
        dcts, listified = listify(dct)
        objs = [self.parse(d) for d in dcts]
        results = unlistify(objs, listified)
        return results

    def add_type(self, type_name, type_function):
        if type_name in self.type_dispatch:
            raise RuntimeError("Already exists")
        self.type_dispatch[type_name] = type_function



CATEGORY_ALIASES = {
    "cv": ["cvs"],
    "volume": ["states", "initial_state", "final_state"],
    "engine": ["engines"],
}

CANONICAL_CATEGORY = {e: k for k, v in CATEGORY_ALIASES.items() for e in v}

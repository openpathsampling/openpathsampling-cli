import os
import importlib
import yaml

from collections import namedtuple, abc

import logging

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

class InstanceBuilder:
    # TODO: add schema as an input so we can autogenerate our JSON schema!
    def __init__(self, builder, attribute_table, optional_attributes=None,
                 defaults=None, module=None, remapper=None):
        self.module = module
        self.builder = builder
        self.builder_name = str(self.builder)
        self.attribute_table = attribute_table
        if optional_attributes is None:
            optional_attributes = {}
        self.optional_attributes = optional_attributes
        # TODO use none_to_default
        if remapper is None:
             remapper = lambda x: x
        self.remapper = remapper
        if defaults is None:
            defaults = {}
        self.defaults = defaults
        self.logger = logging.getLogger(f"parser.InstanceBuilder.{builder}")

    def select_builder(self, dct):
        if self.module is not None:
            builder = getattr(importlib.import_module(self.module), self.builder)
        else:
            builder = self.builder
        return builder

    def parse_attrs(self, dct):
        """Parse the user input dictionary to mapping of name to object.

        Parameters
        ----------
        dct: Dict
            User input dictionary (from YAML, JSON, etc.)

        Returns
        -------
        Dict :
            Mapping with the keys relevant to the input dictionary, but
            values are now appropriate inputs for the builder.
        """
        # TODO: support aliases in dct[attr]
        input_dct = self.defaults.copy()
        self.logger.debug(f"defaults: {input_dct}")
        input_dct.update(dct)
        self.logger.debug(f"effective input: {input_dct}")

        new_dct = {}
        for attr, func in self.attribute_table.items():
            try:
                value = input_dct[attr]
            except KeyError:
                raise InputError(f"'{self.builder_name}' missing required "
                                 f"parameter '{attr}'")
            self.logger.debug(f"{attr}: {input_dct[attr]}")
            new_dct[attr] = func(input_dct[attr])

        optionals = set(self.optional_attributes) & set(dct)
        for attr in optionals:
            new_dct[attr] = self.attribute_table[attr](dct[attr])

        return new_dct

    def build(self, new_dct):
        """Build the object from a dictionary with objects as values.

        Parameters
        ----------
        new_dct : Dict
            The output of :method:`.parse_attrs`. This is a mapping of the
            relevant keys to instantiated objects.

        Returns
        -------
        Any :
            The instance for this dictionary.
        """
        builder = self.select_builder(new_dct)
        ops_dct = self.remapper(new_dct)
        self.logger.debug("Building...")
        self.logger.debug(ops_dct)
        obj =  builder(**ops_dct)
        self.logger.debug(obj)
        return obj

    def __call__(self, dct):
        new_dct = self.parse_attrs(dct)
        return self.build(new_dct)


class Parser:
    """Generic parse class; instances for each category"""
    def __init__(self, type_dispatch, label):
        self.type_dispatch = type_dispatch
        self.label = label
        self.named_objs = {}
        self.all_objs = []
        logger_name = f"parser.Parser[{label}]"
        self.logger = logging.getLogger(logger_name)

    def _parse_str(self, name):
        self.logger.debug(f"Looking for '{name}'")
        try:
            return self.named_objs[name]
        except KeyError as e:
            raise e  # TODO: replace with better error

    def _parse_dict(self, dct):
        dct = dct.copy()  # make a local copy
        name = dct.pop('name', None)
        type_name = dct.pop('type')
        self.logger.info(f"Creating {type_name} named {name}")
        obj = self.type_dispatch[type_name](dct)
        obj = self.register_object(obj, name)
        return obj

    def register_object(self, obj, name):
        if name is not None:
            if name in self.named_objs:
                raise RuntimeError("Same name twice")  # TODO improve
            obj = obj.named(name)
            self.named_objs[name] = obj
        obj = obj.named(name)
        self.all_objs.append(obj)
        return obj

    def register_builder(self, builder, name):
        if name in self.type_dispatch:
            raise RuntimeError(f"'{builder.name}' is already registered "
                               f"with {self.label}")
        self.type_dispatch[name] = builder

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

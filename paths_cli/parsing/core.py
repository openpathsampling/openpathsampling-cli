import os
import json
import importlib
import yaml

from collections import namedtuple, abc
import warnings

import logging

from .errors import InputError
from .tools import custom_eval
from paths_cli.utils import import_thing
from paths_cli.plugin_management import OPSPlugin

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

REQUIRED_PARAMETER = object()

class Parameter:
    SCHEMA = "http://openpathsampling.org/schemas/sim-setup/draft01.json"
    def __init__(self, name, loader, *, json_type=None, description=None,
                 default=REQUIRED_PARAMETER, aliases=None):
        if isinstance(json_type, str):
            try:
                json_type = json.loads(json_type)
            except json.decoder.JSONDecodeError:
                # TODO: maybe log this in case it represents an issue?
                pass

        self.name = name
        self.loader = loader
        self._json_type = json_type
        self._description = description
        self.default = default

    @property
    def required(self):
        return self.default is REQUIRED_PARAMETER

    @property
    def json_type(self):
        return self._get_from_loader(self.loader, 'json_type',
                                     self._json_type)

    @property
    def description(self):
        return self._get_from_loader(self.loader, 'description',
                                     self._description)

    @staticmethod
    def _get_from_loader(loader, attr_name, attr):
        if attr is None:
            try:
                attr = getattr(loader, attr_name)
            except AttributeError:
                pass
        return attr

    def __call__(self, *args, **kwargs):
        # check correct call signature here?
        return self.loader(*args, **kwargs)

    def to_json_schema(self, schema_context=None):
        dct = {
            'type': self.json_type,
            'description': self.description,
        }
        return self.name, dct


class Builder:
    """Builder is a wrapper class to simplify writing builder functions.

    When the parsed parameters dictionary matches the kwargs for your class,
    you can create a valid delayed builder function with

    .. code::

        builder = Builder('import_path.for_the.ClassToBuild')

    Additionally, this class provides hooks for functions that run before or
    after the main builder function. This allows many objects to be built by
    implementing simple functions and hooking themn together with Builder.

    Parameters
    ----------
    builder : Union[Callable, str]
        primary callable to build an object, or string representing the
        fully-qualified path to a callable
    remapper : Callable[[Dict], Dict], optional
        callable to remap the the mapping of ???
    after_build : Callable[[Any, Dict], Any], optional
        ccallable to update the created object with any additional
        information from the original dictionary.
    """
    def __init__(self, builder, *, remapper=None, after_build=None):
        if remapper is None:
            remapper = lambda dct: dct
        if after_build is None:
            after_build = lambda obj, dct: obj
        self.remapper = remapper
        self.after_build = after_build
        self.builder = builder

    def __call__(self, **dct):
        # TODO: change this InstanceBuilder.build to make this better
        if isinstance(self.builder, str):
            module, _, func = self.builder.rpartition('.')
            builder = import_thing(module, func)
        else:
            builder = self.builder

        ops_dct = self.remapper(dct.copy())
        obj = builder(**ops_dct)
        after = self.after_build(obj, dct.copy())
        return after


class InstanceBuilder(OPSPlugin):
    """

    Parameters
    ----------
    builder : Callable
        Function that actually creates an instance of this object. Note that
        the :class:`.Builder` class is often a useful tool here (but any
        callable is allowed).
    parameters : List[:class:`.Parameter]
        Descriptions of the paramters for that the builder takes.
    name : str
        Name used in the text input for this object.
    aliases : List[str]
        Other names that can be used.
    requires_ops : Tuple[int, int]
        version of OpenPathSampling required for this functionality
    requires_cli : Tuple[int, int]
        version of the OPS CLI requires for this functionality
    """
    SCHEMA = "http://openpathsampling.org/schemas/sim-setup/draft01.json"
    parser_name = None
    error_on_duplicate = False  # TODO: temporary
    def __init__(self, builder, parameters, name=None, aliases=None,
                 requires_ops=(1, 0), requires_cli=(0, 3)):
        super().__init__(requires_ops, requires_cli)
        self.aliases = aliases
        self.attribute_table = {p.name: p.loader for p in parameters
                                if p.required}
        self.optional_attributes = {p.name: p.loader for p in parameters
                                    if not p.required}
        self.defaults = {p.name: p.default for p in parameters
                         if not p.required}
        self.name = name
        self.builder = builder
        self.builder_name = str(self.builder)
        self.parameters = parameters
        self.logger = logging.getLogger(f"parser.InstanceBuilder.{builder}")

    @property
    def schema_name(self):
        if not self.name.endswith(self.parser_name):
            schema_name = f"{self.name}-{self.object_type}"
        else:
            schema_name = self.parser_name
        return schema_name

    def to_json_schema(self, schema_context=None):
        parameters = dict(p.to_json_schema() for p in self.parameters)
        properties = {
            'name': {'type': 'string'},
            'type': {'type': 'string',
                     'enum': [self.name]},
        }
        properties.update(parameters)
        required = [p.name for p in self.parameters if p.required]
        dct = {
            'properties': properties,
            'required': required,
        }
        return self.schema_name, dct

    def parse_attrs(self, dct):
        """Parse the user input dictionary to mapping of name to object.

        This changes the values in the key-value pairs we get from the file
        into objects that are suitable as input to a function. Further
        remapping of keys is performed by the builder.

        Parameters
        ----------
        dct: Dict
            User input dictionary (from YAML, JSON, etc.)

        Returns
        -------
        Dict :
            Mapping with the keys from the input dictionary, but values are
            now appropriate inputs for the builder.
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
            new_dct[attr] = self.optional_attributes[attr](dct[attr])

        return new_dct

    def __call__(self, dct):
        ops_dct = self.parse_attrs(dct)
        self.logger.debug("Building...")
        self.logger.debug(ops_dct)
        obj =  self.builder(**ops_dct)
        self.logger.debug(obj)
        return obj


class Parser:
    """Generic parse class; instances for each category"""
    error_on_duplicate = False  # TODO: temporary
    def __init__(self, type_dispatch, label):
        if type_dispatch is None:
            type_dispatch = {}
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
                raise InputError(f"An object of type {self.name} and name "
                                 f"{name} already exists.")
            obj = obj.named(name)
            self.named_objs[name] = obj
        obj = obj.named(name)
        self.all_objs.append(obj)
        return obj

    def register_builder(self, builder, name):
        if name in self.type_dispatch:
            msg = (f"'{builder.name}' is already registered "
                   f"with {self.label}")
            if self.error_on_duplicate:
                raise RuntimeError(msg)
            else:
                warnings.warn(msg)
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

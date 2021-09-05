import pytest
from unittest.mock import Mock, patch

import os

import numpy.testing as npt

from paths_cli.parsing.core import *

class TestParameter:
    def setup(self):
        self.loader = Mock(
            return_value='foo',
            json_type='string',
            description="string 'foo'",
        )

    def test_parameter_info_in_loader(self):
        # if parameter doesn't give json_type/description, but the
        # loader does, then we return what the loader says
        parameter = Parameter(name='foo_param',
                              loader=self.loader)
        assert parameter.name == 'foo_param'
        assert parameter.loader() == "foo"
        assert parameter.json_type == "string"
        assert parameter.description == "string 'foo'"

    def test_parameter_info_local(self):
        # if parameter and loader both give json_type/description, then the
        # value given by the parameter takes precendence
        parameter = Parameter(name='foo_param',
                              loader=self.loader,
                              json_type='int',  # it's a lie!
                              description='override')
        assert parameter.name == 'foo_param'
        assert parameter.loader() == "foo"
        assert parameter.json_type == "int"
        assert parameter.description == "override"

    def test_parameter_info_none(self):
        # if neither parameter nor loader define json_type/description, then
        # we should return None for those
        parameter = Parameter(name="foo_param",
                              loader=lambda: "foo")
        assert parameter.name == 'foo_param'
        assert parameter.loader() == "foo"
        assert parameter.json_type is None
        assert parameter.description is None

    @pytest.mark.parametrize('is_required', [True, False])
    def test_required(self, is_required):
        if is_required:
            parameter = Parameter(name="foo_param", loader=self.loader)
        else:
            parameter = Parameter(name="foo_param", loader=self.loader,
                                  default="bar")

        assert parameter.required == is_required

    def test_call(self):
        # calling the parameter object should call its loader
        # TODO: maybe check that we pass arguments along correctly?
        parameter = Parameter(name="foo_param", loader=self.loader)
        assert parameter() == "foo"

    def test_to_json_schema(self):
        # to_json_schema should return the expected values
        parameter = Parameter(name="foo_param",
                              loader=self.loader)
        expected = {'type': 'string',
                    'description': "string 'foo'"}
        assert parameter.to_json_schema() == ("foo_param", expected)


class TestBuilder:
    @staticmethod
    def _callable(string):
        return "".join(reversed(string))

    def test_with_remapper(self):
        # a builder that includes a remapping should use the remapper before
        # the builder callable
        def local_remapper(dct):
            dct['string'] = dct['string'][:-1]
            return dct

        builder = Builder(self._callable, remapper=local_remapper)
        assert builder(string="foo") == "of"

    def test_imported_builder(self):
        # a builder that takes a string to define its builder callable
        # should import that callable, and use it for its call method
        cwd = os.getcwd()
        builder = Builder('os.getcwd')
        assert builder() == cwd

    def test_callable_builder(self):
        # a builder that takes a callable as its builder should use that for
        # its call method
        builder = Builder(self._callable)
        assert builder(string="foo") == "oof"

    def test_with_after_build(self):
        # a builder with an after_build parameter should use that after the
        # builder callable
        def local_after(obj, dct):
            return obj[:-1] + dct['string']

        builder = Builder(self._callable, after_build=local_after)
        assert builder(string="foo") == "oofoo"

class TestInstanceBuilder:
    @staticmethod
    def _builder(req_param, opt_default=10, opt_override=100):
        return f"{req_param}, {opt_default}, {opt_override}"

    def setup(self):
        identity = lambda x: x
        self.parameters = [
            Parameter('req_param', identity, json_type="string"),
            Parameter('opt_default', identity, json_type="int", default=10),
            Parameter('opt_override', identity, json_type='int',
                      default=100)
        ]
        self.instance_builder = InstanceBuilder(
            self._builder,
            self.parameters,
            name='demo',
            aliases=['foo', 'bar'],
        )
        self.instance_builder.parser_name = 'demo'
        self.input_dict = {'req_param': "qux", 'opt_override': 25}

    def test_to_json_schema(self):
        # to_json_schema should create a valid JSON schema entry for this
        # instance builder
        # TODO: this may change as I better understand JSON schema. Details
        # of the JSON schema API aren't locked until I can build docs from
        # our schema.
        expected_schema = {
            'properties': {
                'name': {'type': 'string'},
                'type': {'type': 'string',
                         'enum': ['demo']},
                'req_param': {'type': 'string', 'description': None},
                'opt_default': {'type': 'int', 'description': None},
                'opt_override': {'type': 'int', 'description': None},
            },
            'required': ['req_param'],
        }
        name, schema =  self.instance_builder.to_json_schema()
        assert name == 'demo'
        assert expected_schema['required'] == schema['required']
        assert expected_schema['properties'] == schema['properties']

    def test_parse_attrs(self):
        # parse_attrs should create a dictionary with correct objects in the
        # attributes from the input dictionary
        expected = {'req_param': "qux", 'opt_override': 25}
        # note that the parameter where we use the default value isn't
        # listed: the default value should match the default used in the
        # code, though!
        assert self.instance_builder.parse_attrs(self.input_dict) == expected

    def test_parse_attrs_parser_integration(self):
        # parse_attrs gives the same object as already existing in a parser
        # if one of the parameters uses that parser to load a named object
        pytest.skip()

    def test_parse_attrs_missing_required(self):
        # an InputError should be raised if a required parameter is missing
        input_dict = {'opt_override': 25}
        with pytest.raises(InputError, match="missing required"):
            self.instance_builder.parse_attrs(input_dict)

    def test_call(self):
        # calling the instance builder should create the object
        expected = "qux, 10, 25"
        assert self.instance_builder(self.input_dict) == expected


class TestParser:
    def test_parse_str(self):
        # parse_str should load a known object with the input name
        pytest.skip()

    def test_parse_str_error(self):
        # if parse_str is given a name that is not known, an InputError
        # should be raised
        pytest.skip()

    def test_parse_dict(self):
        # parse_dct should create the object from the input dict
        pytest.skip()

    def test_register_object_named(self):
        # when registered, a named object should register with the all_objs
        # list and with the named_objs dict
        pytest.skip()

    def test_register_object_unnamed(self):
        # when registered, an unnamed object should register with the
        # all_objs list and leave the named_objs dict unchanged
        pytest.skip()

    def test_register_object_duplicate(self):
        # if an attempt is made to register an object with a name that is
        # already in use, an InputError should be raised, and the object
        # should not register with either all_objs or named_objs
        pytest.skip()

    def test_register_builder(self):
        pytest.skip()

    def test_register_builder_duplicate(self):
        pytest.skip()

    @pytest.mark.parametrize('input_type', ['str', 'dict'])
    def test_parse(self, input_type):
        pytest.skip()

    @pytest.mark.parametrize('as_list', [True, False])
    def test_call(self, as_list):
        pytest.skip()

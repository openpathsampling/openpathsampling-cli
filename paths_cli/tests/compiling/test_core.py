import pytest
from unittest.mock import Mock, patch

import os

import numpy.testing as npt

from paths_cli.compiling.core import *
from paths_cli.compiling import compiler_for
from paths_cli.tests.compiling.utils import mock_compiler

class MockNamedObject:
    # used in the tests for CategoryCompiler._compile_dict and
    # CategoryCompiler.register_object
    def __init__(self, data):
        self.data = data
        self.name = None

    def named(self, name):
        self.name = name
        return self

def mock_named_object_factory(dct):
    return MockNamedObject(**dct)


class TestParameter:
    def setup_method(self):
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

class TestInstanceCompilerPlugin:
    @staticmethod
    def _builder(req_param, opt_default=10, opt_override=100):
        return f"{req_param}, {opt_default}, {opt_override}"

    def setup_method(self):
        identity = lambda x: x
        self.parameters = [
            Parameter('req_param', identity, json_type="string"),
            Parameter('opt_default', identity, json_type="int", default=10),
            Parameter('opt_override', identity, json_type='int',
                      default=100)
        ]
        self.instance_builder = InstanceCompilerPlugin(
            self._builder,
            self.parameters,
            name='demo',
            aliases=['foo', 'bar'],
        )
        self.instance_builder.category = 'demo'
        self.input_dict = {'req_param': "qux", 'opt_override': 25}

    def test_schema_name(self):
        assert self.instance_builder.schema_name == 'demo'
        self.instance_builder.category = 'foo'
        assert self.instance_builder.schema_name == 'demo-foo'
        self.instance_builder.name = 'demo-foo'
        assert self.instance_builder.schema_name == 'demo-foo'


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

    def test_compile_attrs(self):
        # compile_attrs should create a dictionary with correct objects in
        # the attributes from the input dictionary
        expected = {'req_param': "qux", 'opt_override': 25}
        # note that the parameter where we use the default value isn't
        # listed: the default value should match the default used in the
        # code, though!
        compile_attrs = self.instance_builder.compile_attrs
        assert compile_attrs(self.input_dict) == expected

    def test_compile_attrs_compiler_integration(self):
        # compile_attrs gives the existing named object (is-identity) if one
        # of the parameters uses that compiler to load a named object
        user_input = {'foo': 'named_foo'}
        # full_input = {'foo': {'name': 'named_foo',
        #                       'type': 'baz',
        #                       'bar': 'should see this'}}
        bar_plugin = InstanceCompilerPlugin(
            builder=lambda foo: 'in bar: should not see this',
            parameters=[Parameter('foo', compiler_for('foo'))],
        )
        foo_plugin = InstanceCompilerPlugin(
            builder=lambda: 'in foo: should not see this',
            parameters=[],
        )
        named_objs = {'named_foo': 'should see this'}
        type_dispatch = {'baz': foo_plugin}
        PATCH_LOC = 'paths_cli.compiling.root_compiler._COMPILERS'
        compiler = mock_compiler('foo', type_dispatch=type_dispatch,
                                 named_objs=named_objs)
        with patch.dict(PATCH_LOC, {'foo': compiler}):
            compiled = bar_plugin.compile_attrs(user_input)

        # maps attr name 'foo' to the previous existing object
        assert compiled == {'foo': 'should see this'}

    def test_compile_attrs_missing_required(self):
        # an InputError should be raised if a required parameter is missing
        input_dict = {'opt_override': 25}
        with pytest.raises(InputError, match="missing required"):
            self.instance_builder.compile_attrs(input_dict)

    def test_call(self):
        # calling the instance builder should create the object
        expected = "qux, 10, 25"
        assert self.instance_builder(self.input_dict) == expected


class TestCategoryCompiler:
    def setup_method(self):
        self.compiler = CategoryCompiler(
            {'foo': mock_named_object_factory},
            'foo_compiler'
        )

    def _mock_register_obj(self):
        obj = "bar"
        self.compiler.all_objs.append(obj)
        self.compiler.named_objs['foo'] = obj

    def test_compile_str(self):
        # compile_str should load a known object with the input name
        self._mock_register_obj()
        assert self.compiler._compile_str('foo') == "bar"

    def test_compile_str_error(self):
        # if compile_str is given a name that is not known, an InputError
        # should be raised
        self._mock_register_obj()
        with pytest.raises(InputError, match="Unable to find"):
            self.compiler._compile_str('baz')

    @pytest.mark.parametrize('named', [True, False])
    def test_compile_dict(self, named):
        # compile_dct should create the object from the input dict
        input_dict = {'type': 'foo', 'data': "qux"}
        if named:
            input_dict['name'] = 'bar'

        obj = self.compiler._compile_dict(input_dict)
        assert obj.data == "qux"
        name = {True: 'bar', False: None}[named]
        assert obj.name == name

    def test_register_object_named(self):
        # when registered, a named object should register with the all_objs
        # list and with the named_objs dict
        obj = MockNamedObject('foo')
        assert obj.name is None
        assert self.compiler.all_objs == []
        assert self.compiler.named_objs == {}
        obj = self.compiler.register_object(obj, 'bar')
        assert obj.name == 'bar'
        assert self.compiler.all_objs == [obj]
        assert self.compiler.named_objs == {'bar': obj}

    def test_register_object_unnamed(self):
        # when registered, an unnamed object should register with the
        # all_objs list and leave the named_objs dict unchanged
        obj = MockNamedObject('foo')
        assert obj.name is None
        assert self.compiler.all_objs == []
        assert self.compiler.named_objs == {}
        obj = self.compiler.register_object(obj, None)
        assert obj.name is None
        assert self.compiler.all_objs == [obj]
        assert self.compiler.named_objs == {}

    def test_register_object_duplicate(self):
        # if an attempt is made to register an object with a name that is
        # already in use, an InputError should be raised, and the object
        # should not register with either all_objs or named_objs
        obj = MockNamedObject('foo').named('bar')
        self.compiler.named_objs['bar'] = obj
        self.compiler.all_objs.append(obj)
        obj2 = MockNamedObject('baz')
        with pytest.raises(InputError, match="already exists"):
            self.compiler.register_object(obj2, 'bar')

        assert self.compiler.named_objs == {'bar': obj}
        assert self.compiler.all_objs == [obj]
        assert obj2.name is None

    def test_register_builder(self):
        # a new builder can be registered and used, if it has a new name
        assert len(self.compiler.type_dispatch) == 1
        assert 'bar' not in self.compiler.type_dispatch
        self.compiler.register_builder(lambda dct: 10, 'bar')
        assert len(self.compiler.type_dispatch) == 2
        assert 'bar' in self.compiler.type_dispatch
        input_dict = {'type': 'bar'}
        assert self.compiler(input_dict) == 10

    def test_register_builder_duplicate(self):
        # if an attempt is made to registere a builder with a name that is
        # already in use, a RuntimeError is raised
        orig = self.compiler.type_dispatch['foo']
        with pytest.raises(RuntimeError, match="already registered"):
            self.compiler.register_builder(lambda dct: 10, 'foo')

        assert self.compiler.type_dispatch['foo'] is orig

    def test_register_builder_identical(self):
        # if an attempt is made to register a builder that has already been
        # registered, nothin happens (since it is already registered)
        orig = self.compiler.type_dispatch['foo']
        self.compiler.register_builder(orig, 'foo')

    @staticmethod
    def _validate_obj(obj, input_type):
        if input_type == 'str':
            assert obj == 'bar'
        elif input_type == 'dict':
            assert obj.data == 'qux'
        else:  # -no-cov-
            raise RuntimeError("Error in test setup")

    @pytest.mark.parametrize('input_type', ['str', 'dict'])
    def test_compile(self, input_type):
        # the compile method should work whether the input is a dict
        # representing an object to be compiled or string name for an
        # already-compiled object
        self._mock_register_obj()
        input_data = {
            'str': 'foo',
            'dict': {'type': 'foo', 'data': 'qux'}
        }[input_type]
        obj = self.compiler.compile(input_data)
        self._validate_obj(obj, input_type)

    @pytest.mark.parametrize('input_type', ['str', 'dict'])
    @pytest.mark.parametrize('as_list', [True, False])
    def test_call(self, input_type, as_list):
        # the call method should work whether the input is a single object
        # or a list of objects (as well as whether string or dict)
        self._mock_register_obj()
        input_data = {
            'str': 'foo',
            'dict': {'type': 'foo', 'data': 'qux'}
        }[input_type]
        if as_list:
            input_data = [input_data]

        obj = self.compiler(input_data)
        if as_list:
            assert isinstance(obj, list)
            assert len(obj) == 1
            obj = obj[0]
        self._validate_obj(obj, input_type)

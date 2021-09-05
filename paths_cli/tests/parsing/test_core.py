import pytest
from unittest.mock import Mock, patch

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
    def test_with_remapper(self):
        # a builder that includes a remapping should use the remapper before
        # the builder callable
        pytest.skip()

    def test_imported_builder(self):
        # a builder that takes a string to define its builder callable
        # should import that callable, and use it for its call method
        pytest.skip()

    def test_callable_builder(self):
        # a builder that takes a callable as its builder should use that for
        # its call method
        pytest.skip()

    def test_with_after_build(self):
        # a builder with an after_build parameter should use that after the
        # builder callable
        pytest.skip()

class TestInstanceBuilder:
    def test_to_json_schema(self):
        # to_json_schema should create a valid JSON schema entry for this
        # instance builder
        pytest.skip()

    def test_parse_attrs(self):
        # parse_attrs should create a dictionary with correct objects in the
        # attributes from the input dictionary
        pytest.skip()

    def test_parse_attrs_missing_required(self):
        # an InputError should be raised if a required parameter is missing
        pytest.skip()

    def test_call(self):
        # calling the instance builder should create the object
        pytest.skip()


import pytest
from unittest import mock
import io

from paths_cli.compiling._gendocs.docs_generator import *
from paths_cli.compiling._gendocs import DocCategoryInfo

from paths_cli.compiling import Parameter, InstanceCompilerPlugin
from paths_cli.compiling.core import CategoryCompiler

class TestDocsGenerator:
    def setup_method(self):
        self.required_parameter = Parameter(
            name="req_param",
            loader=None,
            json_type="string",
            description="req_desc",
        )
        self.optional_parameter = Parameter(
            name="opt_param",
            loader=None,
            json_type="string",
            description="opt_desc",
            default="foo",
        )
        self.plugin = InstanceCompilerPlugin(
            builder=None,
            parameters=[self.required_parameter,
                        self.optional_parameter],
            name="object_plugin",
            description="object_plugin_desc",
        )
        self.category = CategoryCompiler(
            type_dispatch=None,
            label="category",
        )
        self.category.register_builder(self.plugin, self.plugin.name)

        self.generator = DocsGenerator(
            {'category': DocCategoryInfo(header="Header",
                                         description="category_desc")}
        )
        self.param_strs = ['req_param', 'req_desc', 'opt_param', 'opt_desc']
        self.obj_plugin_strs = [
            ".. _category--object_plugin:",
            "object_plugin\n-------------\n",
            "object_plugin_desc",
        ]
        self.category_strs = [
            ".. _compiling--category:",
            "Header\n======\n",
            ".. contents:: :local:",
            "\ncategory_descThe following types are available:\n",
        ]

    @pytest.mark.parametrize('param_type', ['req', 'opt'])
    def test_format_parameter(self, param_type):
        # when formatting individual parameters, we should obtain the
        # correct RST string
        param = {'req': self.required_parameter,
                 'opt': self.optional_parameter}[param_type]
        expected = {  # NOTE: these can change without breaking API
            'req': "* **req_param** (string) - req_desc (required)\n",
            'opt': "* **opt_param** (string) - opt_desc\n",
        }[param_type]
        type_str = f" ({param.json_type})"
        result = self.generator.format_parameter(param, type_str=type_str)
        assert result == expected

    @pytest.mark.parametrize('label', ['category', 'unknown'])
    def test_get_cat_info(self, label):
        # getting a DocCategoryInfo should either give the result from the
        # config or give the best-guess default
        category = {
            'category': self.category,
            'unknown': CategoryCompiler(type_dispatch=None,
                                        label="unknown"),
        }[label]
        expected = {
            'category': DocCategoryInfo(header="Header",
                                        description="category_desc"),
            'unknown': DocCategoryInfo(header='unknown')
        }[label]
        assert self.generator._get_cat_info(category) == expected

    def test_generate_category_rst(self):
        # generating RST for a category plugin should include the expected
        # RST strings
        result = self.generator.generate_category_rst(self.category)
        expected_strs = (self.param_strs + self.obj_plugin_strs
                         + self.category_strs)
        for string in expected_strs:
            assert string in result

    @pytest.mark.parametrize('type_required', [True, False])
    def test_generate_plugin_rst(self, type_required):
        # generating RST for an object plugin should include the expected
        # RST strings
        result = self.generator.generate_plugin_rst(
            self.plugin,
            self.category.label,
            type_required=type_required
        )
        for string in self.param_strs + self.obj_plugin_strs:
            assert string in result

        type_str = "**type** - type identifier; must exactly match"
        if type_required:
            assert type_str in result
        else:
            assert type_str not in result

    @pytest.mark.parametrize('inputs,expected', [
        ("Collective Variables", "collective_variables.rst"),
    ])
    def test_get_filename(self, inputs, expected):
        # filenames creating from a DocCategoryInfo (using _get_filename)
        # should give expected filenames
        cat_info = DocCategoryInfo(inputs)
        assert self.generator._get_filename(cat_info) == expected

    @pytest.mark.parametrize('stdout', [True, False])
    def test_generate(self, stdout):
        base_loc = "paths_cli.compiling._gendocs.docs_generator."
        if stdout:
            mock_loc = base_loc + "sys.stdout"
            mock_obj = mock.Mock()
        else:
            mock_loc = base_loc + "open"
            mock_obj = mock.mock_open()

        mock_generate_category = mock.Mock(return_value="foo")
        self.generator.generate_category_rst =mock_generate_category

        with mock.patch(mock_loc, mock_obj):
            self.generator.generate([self.category], stdout=stdout)

        mock_generate_category.assert_called_once()
        if not stdout:
            mock_obj.assert_called_once_with('header.rst', 'w')

        write = mock_obj.write if stdout else mock_obj().write
        write.assert_called_once_with("foo")

import pytest
from unittest import mock
from paths_cli.wizard.plugin_classes import *
from paths_cli.tests.wizard.test_helper import mock_wizard
from paths_cli.wizard.standard_categories import Category
from paths_cli.wizard.parameters import WizardParameter, ProxyParameter

from paths_cli import compiling

import openpathsampling as paths


class TestLoadOPS:
    def test_init_by_category(self):
        # when LoadFromOPS does not include explicit obj_name or store_name,
        # the relevant info should be loaded from the category
        # (note: testing for errors here is part of tests for
        # get_category_info)
        cat = Category(name='foo',
                       singular='singular',
                       plural='plural',
                       storage='store')
        CAT_LOC = "paths_cli.wizard.standard_categories.CATEGORIES"
        with mock.patch.dict(CAT_LOC, {'foo': cat}):
            loader = LoadFromOPS('foo')

        assert loader.obj_name == 'singular'
        assert loader.store_name == 'store'

    def test_call(self):
        # the created object should call the load_from_ops method with
        # appropriate parameters (note that the test of load_from_ops is
        # done separately)
        loader = LoadFromOPS("cat_name", obj_name='foo', store_name='foos')
        wiz = mock_wizard([])
        mock_load = mock.Mock(return_value="some_object")
        patch_loc = "paths_cli.wizard.plugin_classes.load_from_ops"
        with mock.patch(patch_loc, mock_load):
            result = loader(wiz)

        assert mock_load.called_once_with(wiz, "foos", "foo")
        assert result == "some_object"


@pytest.mark.parametrize('context,instance,default,expected', [
    ('empty', 'method', 'None', ['instance_method']),
    ('empty', 'string', 'None', ['instance_string']),
    ('string', 'method', 'None', ['context_string']),
    ('method', 'method', 'None', ['context_method']),
    ('empty', 'empty', 'method', ['default_method']),
    ('empty', 'empty', 'string', ['default_string']),
    ('empty', 'empty', 'None', []),
])
def test_get_text_from_context(context, instance, default, expected):
    def make_method(carrier):
        def method(wizard, context, *args, **kwargs):
            return f"{carrier}_method"
        return method

    context = {'empty': {},
               'string': {'foo': 'context_string'},
               'method': {'foo': make_method('context')}}[context]
    instance = {'string': 'instance_string',
                'method': make_method('instance'),
                'empty': None}[instance]
    default = {'method': make_method('default'),
               'string': "default_string",
               'None': None}[default]

    wiz = mock_wizard([])

    result = get_text_from_context("foo", instance, default, wiz, context)
    assert result == expected


class TestWizardObjectPlugin:
    def setup(self):
        self.plugin = WizardObjectPlugin(
            name="foo",
            category="foo_category",
            builder=lambda wizard, context: "foo_obj",
            intro="foo intro",
            summary="foo summary",
        )

    def test_default_summarize(self):
        wizard = mock_wizard([])
        context = {}
        result = "foo"
        summ = self.plugin.default_summarize(wizard, context, result)
        assert len(summ) == 1
        assert "Here's what we'll make" in summ[0]
        assert "foo" in summ[0]

    def test_call(self):
        wizard = mock_wizard([])
        res = self.plugin(wizard)
        assert "foo intro" in wizard.console.log_text
        assert "foo summary" in wizard.console.log_text
        assert res == "foo_obj"

    def test_call_with_prereq(self):
        def prereq(wizard):
            wizard.say("Running prereq")
            return {'prereq': ['results']}

        plugin = WizardObjectPlugin(
            name="foo",
            category="foo_category",
            builder=lambda wizard, context: "foo_obj",
            prerequisite=prereq,
        )

        wizard = mock_wizard([])
        result = plugin(wizard, context={})
        assert result == "foo_obj"
        assert "Running prereq" in wizard.console.log_text


class TestWizardParameterObjectPlugin:
    class MyClass(paths.netcdfplus.StorableNamedObject):
        def __init__(self, foo, bar):
            self.foo = foo
            self.bar = bar

    def setup(self):
        self.parameters = [
            WizardParameter(name="foo",
                            ask="Gimme a foo!",
                            loader=int),
            WizardParameter(name="bar",
                            ask="Tell me bar!",
                            loader=str)
        ]
        self.plugin = WizardParameterObjectPlugin(
            name="baz",
            category="baz_cat",
            parameters=self.parameters,
            builder=self.MyClass,
        )
        self.wizard = mock_wizard(['11', '22'])

    def _check_call(self, result, wizard):
        assert isinstance(result, self.MyClass)
        assert result.foo == 11
        assert result.bar == "22"
        assert "Gimme a foo" in wizard.console.log_text
        assert "Tell me bar" in wizard.console.log_text

    def test_call(self):
        result = self.plugin(self.wizard)
        self._check_call(result, self.wizard)

    def test_from_proxies(self):
        object_compiler = compiling.InstanceCompilerPlugin(
            builder=self.MyClass,
            parameters=[
                compiling.Parameter(name="foo", loader=int),
                compiling.Parameter(name="bar", loader=str),
            ]
        )
        proxies = [
            ProxyParameter(name="foo",
                           ask="Gimme a foo!"),
            ProxyParameter(name="bar",
                           ask="Tell me bar!"),

        ]
        plugin = WizardParameterObjectPlugin.from_proxies(
            name="baz",
            category="baz_cat",
            parameters=proxies,
            compiler_plugin=object_compiler
        )
        result = plugin(self.wizard)
        self._check_call(result, self.wizard)


class TestCategoryHelpFunc:
    pass


class TestWrapCategory:
    pass

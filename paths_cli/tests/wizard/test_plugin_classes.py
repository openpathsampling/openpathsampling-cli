import pytest
from unittest import mock
from paths_cli.wizard.plugin_classes import *
from paths_cli.tests.wizard.mock_wizard import mock_wizard
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

        mock_load.assert_called_once_with(wiz, "foos", "foo")
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
    # get_text_from_context should obtain the appropriate resulting wizard
    # text regardless for various combinations of its inputs, which can be
    # None (empty) or a method to be called or a string to be used directly,
    # and can be selected from context (highest precedence) or a value
    # typically associated with the instance (next precedence) or the class
    # default (lowest precedence).
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
    def setup_method(self):
        self.plugin = WizardObjectPlugin(
            name="foo",
            category="foo_category",
            builder=lambda wizard, context: "foo_obj",
            intro="foo intro",
            summary="foo summary",
        )

    def test_default_summarize(self):
        # ensure that we get the correct output from default_summarize
        wizard = mock_wizard([])
        context = {}
        result = "foo"
        summ = self.plugin.default_summarize(wizard, context, result)
        assert len(summ) == 1
        assert "Here's what we'll make" in summ[0]
        assert "foo" in summ[0]

    def test_call(self):
        # check that calling the plugin creates the correct object and
        # outputs intro/summary to the wizard
        wizard = mock_wizard([])
        res = self.plugin(wizard)
        assert "foo intro" in wizard.console.log_text
        assert "foo summary" in wizard.console.log_text
        assert res == "foo_obj"

    def test_call_with_prereq(self):
        # ensure that prerequisites get run if they are provided
        def prereq(wizard, context):
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

    def setup_method(self):
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
        # when provided parameters and a builder function, we should get the
        # expected result and log from the wizard
        result = self.plugin(self.wizard)
        self._check_call(result, self.wizard)

    def test_from_proxies(self):
        # when provided proxy parameters and an InstanceCompilerPlugin, we
        # should get the expected result and log from the wizard
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
    def setup_method(self):
        self.category = WrapCategory("foo", "ask foo")
        self.plugin = WizardObjectPlugin(
            name="bar",
            category="foo",
            builder=lambda wizard, context: "bar_obj",
            description="bar_help",
        )
        self.category.choices['bar'] = self.plugin
        self.helper = CategoryHelpFunc(
            category=self.category,
            basic_help="help for foo category"
        )

    @pytest.mark.parametrize('input_type', ['int', 'str'])
    def test_call(self, input_type):
        # we should get the help for a category item whether it is requested
        # by number or by name
        inp = {'int': "1", 'str': "bar"}[input_type]
        assert self.helper(inp, {}) == "bar_help"

    @pytest.mark.parametrize('input_type', ['int', 'str'])
    def test_call_no_description(self, input_type):
        # when no description for a category item is provided, we should get
        # the "no help available" message
        plugin = WizardObjectPlugin(
            name="bar",
            category="foo",
            builder=lambda wizard, context: "bar_obj"
        )
        # override with local plugin, no description
        self.category.choices['bar'] = plugin

        inp = {'int': "1", 'str': "bar"}[input_type]
        assert self.helper(inp, {}) == "Sorry, no help available for 'bar'."

    def test_call_empty(self):
        # when called with the empty string, we should get the help for the
        # category
        assert self.helper("", {}) == "help for foo category"

    def test_call_empty_no_description(self):
        # when called with empty string and no category help defined, we
        # should get the "no help available" message
        helper = CategoryHelpFunc(category=self.category)
        assert helper("", {}) == "Sorry, no help available for foo."

    @pytest.mark.parametrize('input_type', ['int', 'str'])
    def test_bad_arg(self, input_type):
        # if a bad argument is passed to help, the help should return None
        # (causing the error message to be issued higher in the stack)
        inp = {'int': "2", 'str': "baz"}[input_type]
        assert self.helper(inp, {}) is None


class TestWrapCategory:
    def setup_method(self):
        self.wrapper = WrapCategory("foo", "ask foo", intro="intro_foo")
        self.plugin_no_format = WizardObjectPlugin(
            name="bar",
            category="foo",
            builder=lambda wizard, context: "bar_obj",
        )
        self.plugin_format = WizardObjectPlugin(
            name="bar",
            category="foo",
            prerequisite=lambda wizard, context: {'baz': context['baz']},
            builder=(lambda wizard, prereq:
                     "bar_obj baz={baz}".format(**prereq)),
        )

    @pytest.mark.parametrize('input_type', ['method', 'None'])
    def test_set_context(self, input_type):
        # set_context should create a new context dict if given a method to
        # create a new context, or return the is-identical input if give no
        # method
        old_context = {'baz': 'qux'}
        new_context = {'foo': 'bar'}
        set_context = {
            'method': lambda wizard, context, selected: new_context,
            'None': None,
        }[input_type]
        expected = {
            'method': new_context,
            'None': old_context,
        }[input_type]
        wrapper = WrapCategory("foo", "ask foo", set_context=set_context)
        wizard = mock_wizard([])
        context = wrapper._set_context(wizard, old_context, selected=None)
        assert context == expected
        if input_type == 'None':
            assert context is expected

    def test_register_plugin(self):
        # register_plugin should add the plugin to the choices
        assert len(self.wrapper.choices) == 0
        self.wrapper.register_plugin(self.plugin_no_format)
        assert len(self.wrapper.choices) == 1
        assert self.wrapper.choices['bar'] == self.plugin_no_format

    def test_register_plugin_duplicate(self):
        self.wrapper.choices['bar'] = self.plugin_no_format
        with pytest.raises(WizardObjectPluginRegistrationError,
                           match="already been registered"):
            self.wrapper.register_plugin(self.plugin_format)

    @pytest.mark.parametrize('input_type', ['method', 'format', 'string'])
    def test_get_ask(self, input_type):
        # wrapper.get_ask should create the appropriate input string whether
        # it is a plain string, or a string that is formatted by the context
        # dict, or a method that takes wizard and context to return a string
        ask = {
            'method': lambda wizard, context: f"Bar is {context['bar']}",
            'format': "Bar is {bar}",
            'string': "Bar is 10"
        }[input_type]
        context = {'bar': 10}
        wrapper = WrapCategory("foo", ask)
        wizard = mock_wizard([])
        ask_string = wrapper._get_ask(wizard, context)
        assert ask_string == "Bar is 10"

    @pytest.mark.parametrize('context_type', ['None', 'dict'])
    def test_call(self, context_type):
        # test that the call works both when the context is unimportant (and
        # not given) and when the context is used in the builder
        context = {
            'None': None,
            'dict': {'baz': 11},
        }[context_type]
        expected = {
            'None': "bar_obj",
            'dict': "bar_obj baz=11",
        }[context_type]
        self.wrapper.choices['bar'] = {
            'None': self.plugin_no_format,
            'dict': self.plugin_format,
        }[context_type]

        wizard = mock_wizard(['1'])
        result = self.wrapper(wizard, context)
        assert "intro_foo" in wizard.console.log_text
        assert "ask foo" in wizard.console.log_text
        assert "1. bar" in wizard.console.log_text
        assert result == expected

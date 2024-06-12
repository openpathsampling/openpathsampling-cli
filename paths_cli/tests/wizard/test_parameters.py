import pytest
from unittest import mock

from paths_cli.tests.wizard.mock_wizard import mock_wizard
import paths_cli.compiling.core as compiling
from paths_cli.compiling.root_compiler import _CategoryCompilerProxy
from paths_cli.wizard import standard_categories

import openpathsampling as paths

from paths_cli.wizard.parameters import *

class TestWizardParameter:
    @staticmethod
    def _reverse(string):
        return "".join(reversed(string))

    def setup_method(self):
        self.parameter = WizardParameter(
            name='foo',
            ask="How should I {do_what}?",
            loader=self._reverse,
            summarize=lambda string: f"Should be unused. Input: {string}",
        )
        self.wizard = mock_wizard(["bar"])
        self.compiler_plugin = compiling.InstanceCompilerPlugin(
            builder=lambda foo: {'foo': foo, 'bar': bar},
            parameters=[
                compiling.Parameter(name='foo',
                                    loader=lambda x: x),
                compiling.Parameter(name='bar',
                                    loader=_CategoryCompilerProxy('bar'))
            ]
        )

    def test_parameter_call(self):
        # using a normal parameter should call the loader and give expected
        # results
        result = self.parameter(self.wizard, context={'do_what': 'baz'})
        assert result == "rab"
        log = self.wizard.console.log_text
        assert "How should I baz?" in log

    def test_from_proxy_call_standard(self):
        # using a proxy for a normal parameter (not an existing object)
        # should work and give the expected result
        proxy = ProxyParameter(name='foo', ask="ask foo?")
        wizard = mock_wizard(['baz'])
        real_param = WizardParameter.from_proxy(proxy, self.compiler_plugin)
        result = real_param(wizard, context={})
        assert result == "baz"
        assert "ask foo?" in wizard.console.log_text

    def test_from_proxy_call_existing(self):
        # using a proxy parameter that seeks an existing object should work
        # and give the expected result
        proxy = ProxyParameter(name='bar',
                               ask="ask bar?")
        cat = standard_categories.Category(name='bar',
                                           singular='bar',
                                           plural='bars',
                                           storage='bars')
        cat_loc = 'paths_cli.wizard.standard_categories.CATEGORIES'
        get_cat_wiz_loc = ('paths_cli.wizard.plugin_registration'
                           '.get_category_wizard')
        get_cat_wiz_mock = mock.Mock()
        with mock.patch(cat_loc, {'bar': cat}) as p1, \
                mock.patch(get_cat_wiz_loc, get_cat_wiz_mock) as p2:
            parameter = WizardParameter.from_proxy(proxy,
                                                   self.compiler_plugin)
            wizard = mock_wizard(['bar', 'baz'])
            wizard.bars = {'baz': 'qux'}
            result = parameter(wizard, context={})

        assert result == 'qux'
        assert "1. baz" in wizard.console.log_text
        assert "2. Create a new bar" in wizard.console.log_text
        assert "'bar' is not a valid option" in wizard.console.log_text


class TestFromWizardPrerequisite:
    def setup_method(self):
        # For this model, user input should be a string that represents an
        # integer. The self._create method repeats the input string, e.g.,
        # "1" => "11", and wraps the result in self.Wrapper. This is the
        # thing that is actually stored in wizard.store. The self._load_func
        # method converts that to an integer. This is returned from various
        # functions.
        self.prereq = FromWizardPrerequisite(
            name='foo',
            create_func=self._create,
            category='foo_cat',
            n_required=2,
            obj_name='obj_name',
            store_name='store',
            say_create="create one",
            say_finish="now we're done",
            load_func=self._load_func
        )

    class Wrapper(paths.netcdfplus.StorableNamedObject):
        def __init__(self, val):
            super().__init__()
            self.val = val

    def _create(self, wizard):
        as_str = wizard.ask("create_func")
        return self.Wrapper(as_str * 2)

    def _load_func(self, obj):
        return int(obj.val)

    def test_setup_from_category_info(self):
        # when obj_name and store_name are not specified, and the category
        # is known in standard_categories, the obj_name and store_name
        # should be set according to the category name
        cat = standard_categories.Category(name='foo',
                                           singular='singular',
                                           plural='plural',
                                           storage='storage')
        cat_loc = 'paths_cli.wizard.standard_categories.CATEGORIES'
        with mock.patch(cat_loc, {'foo': cat}):
            prereq = FromWizardPrerequisite('foo_obj', ..., 'foo', 1)

        assert prereq.obj_name == "singular"
        assert prereq.store_name == "storage"

    def test_no_load_func(self):
        # if load_func is not provided, then the output of prereq.load_func
        # should be is-identical to its input
        prereq = FromWizardPrerequisite('foo', ..., 'foo_cat', 1,
                                        obj_name='foo', store_name='foos')
        assert prereq.load_func(prereq) is prereq

    def test_create_new(self):
        # the create_new method should return the (integer) value from the
        # load_func, and the Wrapper object should be registered with the
        # wizard as a side-effect. The say_create should appear in logs.
        wiz = mock_wizard(["1", "name1"])
        wiz.store = {}
        obj = self.prereq._create_new(wiz)
        assert obj == 11
        assert len(wiz.store) == 1
        assert wiz.store['name1'].val == "11"
        assert "create one" in wiz.console.log_text

    def test_get_existing(self):
        # the get_existing method should load objects currently in the
        # storage, after passing them through the load_func. This should be
        # done without any statements to the user.
        wiz = mock_wizard([])
        wiz.store = {'bar': self.Wrapper("11"),
                     'baz': self.Wrapper("22")}
        obj = self.prereq._get_existing(wiz)
        assert obj == [11, 22]
        assert wiz.console.log_text == ""

    def test_select_existing(self):
        # select_existing should return the selected result based on
        # existing objects in storage and logs should include question from
        # wizard.obj_selector
        wiz = mock_wizard(['1'])
        wiz.store = {'bar': self.Wrapper("11"),
                     'baz': self.Wrapper("22"),
                     'qux': self.Wrapper("33")}
        obj = self.prereq._select_single_existing(wiz)
        assert obj == 11
        assert "Which obj_name would you" in wiz.console.log_text

    @pytest.mark.parametrize('objs', ['fewer', 'exact', 'more'])
    def test_call(self, objs):
        n_objs = {'fewer': 1, 'exact': 2, 'more': 3}[objs]
        inputs = {'fewer': ['2', 'name2'],
                  'exact': [],
                  'more': ['1', '2']}[objs]

        wrappers = {"name" + i: self.Wrapper(i*2) for i in ['1', '2', '3']}
        items = list(wrappers.items())[:n_objs]

        wiz = mock_wizard(inputs)
        wiz.store = dict(items)

        results = self.prereq(wiz)
        assert len(results) == 1
        assert len(results['foo']) == 2
        assert results['foo'] == [11, 22]
        if objs != 'exact':
            assert "now we're done" in wiz.console.log_text

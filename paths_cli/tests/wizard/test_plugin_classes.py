import pytest
from unittest import mock
from paths_cli.wizard.plugin_classes import *
from paths_cli.tests.wizard.test_helper import mock_wizard
from paths_cli.wizard.standard_categories import Category


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
        pass

    def test_default_summarize(self):
        pytest.skip()

    def test_get_summary(self):
        pytest.skip()

    def test_call(self):
        pytest.skip()




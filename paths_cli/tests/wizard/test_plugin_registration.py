import pytest
from unittest import mock
from paths_cli.wizard.plugin_registration import *
from paths_cli.wizard.plugin_registration import _register_category_plugin
from paths_cli.tests.wizard.mock_wizard import mock_wizard
from paths_cli.plugin_management import OPSPlugin
from paths_cli.wizard.plugin_classes import WrapCategory, WizardObjectPlugin

CAT_PLUGINS_LOC = "paths_cli.wizard.plugin_registration._CATEGORY_PLUGINS"

def _simple_func(wizard, context=None):
    wizard.say("bar")
    return 10

class MockPlugin(OPSPlugin):
    def __init__(self, name='foo', requires_ops=(1, 0), requires_cli=(0, 3)):
        super().__init__(requires_ops, requires_cli)

    def __call__(self, wizard, context):
        return _simple_func(wizard, context)


def test_get_category_wizard():
    # get_category_wizard returns a function that will run a given wizard
    # (even if the specific wizard is only registered at a later point in
    # time)
    func = get_category_wizard('foo')
    wiz = mock_wizard([])
    with mock.patch.dict(CAT_PLUGINS_LOC, {'foo': MockPlugin('foo')}):
        result = func(wiz, {})

    assert result == 10
    assert "bar" in wiz.console.log_text

def test_get_category_wizard_error():
    # if a category plugin of the given name does not exist, an error is
    # raised
    func = get_category_wizard("foo")
    wiz = mock_wizard([])
    with pytest.raises(CategoryWizardPluginRegistrationError,
                       match="No wizard"):
        func(wiz, {})

def test_register_category_plugin():
    # a category plugin can be registered using _register_category_plugin
    plugin = WrapCategory("foo", "ask_foo")
    PLUGINS = {}
    with mock.patch.dict(CAT_PLUGINS_LOC, PLUGINS):
        from paths_cli.wizard.plugin_registration import _CATEGORY_PLUGINS
        assert len(_CATEGORY_PLUGINS) == 0
        _register_category_plugin(plugin)
        assert len(_CATEGORY_PLUGINS) == 1


def test_register_category_plugin_duplicate():
    # if two category plugins try to use the same name, an error is raised
    plugin = WrapCategory("foo", "ask_foo")
    PLUGINS = {"foo": WrapCategory("foo", "foo 2")}
    with mock.patch.dict(CAT_PLUGINS_LOC, PLUGINS):
        with pytest.raises(CategoryWizardPluginRegistrationError,
                           match="already been reserved"):
            _register_category_plugin(plugin)


def test_register_plugins():
    # when we register plugins, category plugins should register as
    # correctly and object plugins should register with the correct category
    # plugins
    cat = WrapCategory("foo", "ask_foo")
    obj = WizardObjectPlugin("bar", "foo", _simple_func)
    PLUGINS = {}
    with mock.patch.dict(CAT_PLUGINS_LOC, PLUGINS):
        from paths_cli.wizard.plugin_registration import _CATEGORY_PLUGINS
        register_plugins([cat, obj])
        assert len(_CATEGORY_PLUGINS) == 1
        assert _CATEGORY_PLUGINS["foo"] == cat

    assert len(cat.choices) == 1
    assert cat.choices['bar'] == obj

def test_register_installed_plugins():
    # mostly a smoke test, but also check that the LoadFromOPS plugin is the
    # last choice in situations where it is a choice
    register_installed_plugins()
    from paths_cli.wizard.plugin_registration import _CATEGORY_PLUGINS
    for cat in ['engine', 'cv']:
        cat_plug = _CATEGORY_PLUGINS[cat]
        choices = list(cat_plug.choices.values())
        assert isinstance(choices[-1], LoadFromOPS)

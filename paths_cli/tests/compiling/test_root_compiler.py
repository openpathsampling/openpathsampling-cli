import pytest
import paths_cli
from paths_cli.compiling.root_compiler import *
from paths_cli.compiling.root_compiler import (
    _canonical_name, _get_compiler, _get_registration_names,
    _register_builder_plugin, _register_compiler_plugin,
    _sort_user_categories, _CategoryCompilerProxy, _COMPILERS, _ALIASES
)
from paths_cli.tests.compiling.utils import mock_compiler
from unittest.mock import Mock, PropertyMock, patch
from paths_cli.compiling.core import (
    CategoryCompiler, InstanceCompilerPlugin
)
from paths_cli.compiling.plugins import CategoryPlugin


### FIXTURES ###############################################################

@pytest.fixture
def foo_compiler():
    return CategoryCompiler(None, 'foo')


@pytest.fixture
def foo_compiler_plugin():
    return CategoryPlugin(Mock(category='foo', __name__='foo'), ['bar'])


@pytest.fixture
def foo_baz_builder_plugin():
    builder = InstanceCompilerPlugin(lambda: "FOO", [], name='baz',
                                     aliases=['qux'])
    builder.category = 'foo'
    return builder


### CONSTANTS ##############################################################

COMPILER_LOC = "paths_cli.compiling.root_compiler._COMPILERS"
BASE = "paths_cli.compiling.root_compiler."


### TESTS ##################################################################

@pytest.mark.parametrize('input_string', ["foo-bar", "FOO_bar", "foo  bar",
                                          "foo_bar", "foo BAR"])
def test_clean_input_key(input_string):
    assert clean_input_key(input_string) == "foo_bar"


@pytest.mark.parametrize('input_name', ['canonical', 'alias'])
def test_canonical_name(input_name):
    compilers = {'canonical': "FOO"}
    aliases = {'alias': 'canonical'}
    with patch.dict(COMPILER_LOC, compilers) as compilers_, \
            patch.dict(BASE + "_ALIASES", aliases) as aliases_:
        assert _canonical_name(input_name) == "canonical"


class TestCategoryCompilerProxy:
    def setup_method(self):
        self.compiler = CategoryCompiler(None, "foo")
        self.compiler.named_objs['bar'] = 'baz'
        self.proxy = _CategoryCompilerProxy('foo')

    def test_proxy(self):
        # (NOT API) the _proxy should be the registered compiler
        with patch.dict(COMPILER_LOC, {'foo': self.compiler}):
            assert self.proxy._proxy is self.compiler

    def test_proxy_nonexisting(self):
        # _proxy should error if the no compiler is registered
        with pytest.raises(RuntimeError, match="No CategoryCompiler"):
            self.proxy._proxy

    def test_named_objs(self):
        # the `.named_objs` attribute should work in the proxy
        with patch.dict(COMPILER_LOC, {'foo': self.compiler}):
            assert self.proxy.named_objs == {'bar': 'baz'}

    def test_call(self):
        # the `__call__` method should work in the proxy
        def _bar_dispatch(dct):
            return dct['baz'] * dct['qux']

        foo_compiler = mock_compiler(
            category='foo',
            type_dispatch={'bar': _bar_dispatch},
        )
        proxy = _CategoryCompilerProxy('foo')
        user_input = {'type': 'bar', 'baz': 'baz', 'qux': 2}
        with patch.dict(COMPILER_LOC, {'foo': foo_compiler}):
            assert proxy(user_input) == "bazbaz"


def test_compiler_for_nonexisting():
    # if nothing is ever registered with the compiler, then compiler_for
    # should error
    compilers = {}
    with patch.dict(COMPILER_LOC, compilers):
        assert 'foo' not in compilers
        proxy = compiler_for('foo')
        assert 'foo' not in compilers
        with pytest.raises(RuntimeError, match="No CategoryCompiler"):
            proxy._proxy


def test_compiler_for_existing(foo_compiler):
    # if a compiler already exists when compiler_for is called, then
    # compiler_for should get that as its proxy
    with patch.dict(COMPILER_LOC, {'foo': foo_compiler}):
        proxy = compiler_for('foo')
        assert proxy._proxy is foo_compiler


def test_compiler_for_unregistered(foo_compiler):
    # if a compiler is registered after compiler_for is called, then
    # compiler_for should use that as its proxy
    proxy = compiler_for('foo')
    with patch.dict(COMPILER_LOC, {'foo': foo_compiler}):
        assert proxy._proxy is foo_compiler


def test_compiler_for_registered_alias(foo_compiler):
    # if compiler_for is registered as an alias, compiler_for should still
    # get the correct compiler
    compilers = {'foo': foo_compiler}
    aliases = {'bar': 'foo'}
    with patch.dict(COMPILER_LOC, compilers) as compilers_, \
            patch.dict(BASE + "_ALIASES", aliases) as aliases_:
        proxy  = compiler_for('bar')
        assert proxy._proxy is foo_compiler


def test_get_compiler_existing(foo_compiler):
    # if a compiler has been registered, then _get_compiler should return the
    # registered compiler
    with patch.dict(COMPILER_LOC, {'foo': foo_compiler}):
        assert _get_compiler('foo') is foo_compiler


def test_get_compiler_nonexisting(foo_compiler):
    # if a compiler has not been registered, then _get_compiler should create
    # the compiler
    with patch.dict(COMPILER_LOC, {}):
        compiler = _get_compiler('foo')
        assert compiler is not foo_compiler  # overkill
        assert compiler.label == 'foo'
        assert 'foo' in _COMPILERS


def test_get_compiler_none():
    # if trying to get the None compiler, the same None compiler should
    # always be returned
    with patch.dict(COMPILER_LOC, {}):
        compiler1 = _get_compiler(None)
        assert compiler1.label is None
        compiler2 = _get_compiler(None)
        assert compiler1 is compiler2


def test_get_compiler_nonstandard_name_multiple():
    # regression test based on real issue -- there was an error where
    # non-canonical names (e.g., names that involved hyphens instead of
    # underscores) would overwrite the previously created compiler instead
    # of getting the identical object
    with patch.dict(COMPILER_LOC, {}):
        c1 = _get_compiler('non-canonical-name')
        c2 = _get_compiler('non-canonical-name')
        assert c1 is c2


@pytest.mark.parametrize('canonical,aliases,expected', [
    ('foo', ['bar', 'baz'], ['foo', 'bar', 'baz']),
    ('foo', ['baz', 'bar'], ['foo', 'baz', 'bar']),
    ('foo', ['foo', 'bar'], ['foo', 'bar']),
])
def test_get_registration_names(canonical, aliases, expected):
    # _get_registration_names should always provide the names in order
    # `canonical, alias1, alias2, ...` regardless of whether `canonical` is
    # also listed in the aliases
    plugin = Mock(aliases=aliases)
    type(plugin).name = PropertyMock(return_value=canonical)
    assert _get_registration_names(plugin) == expected


def test_register_compiler_plugin(foo_compiler_plugin):
    # _register_compiler_plugin should register compilers that don't exist
    compilers = {}
    aliases = {}
    with patch.dict(COMPILER_LOC, compilers) as _compiler, \
                patch.dict(BASE + "_ALIASES", aliases) as _alias:
        assert 'foo' not in compilers
        _register_compiler_plugin(foo_compiler_plugin)
        assert 'foo' in _COMPILERS
        assert 'bar' in _ALIASES

    assert 'foo' not in _COMPILERS


@pytest.mark.parametrize('duplicate_of', ['canonical', 'alias'])
@pytest.mark.parametrize('duplicate_from', ['canonical', 'alias'])
def test_register_compiler_plugin_duplicate(duplicate_of, duplicate_from):
    # if a compiler of the same name exists either in canonical or aliases,
    # _register_compiler_plugin should raise an error

    # duplicate_of: existing
    # duplicate_from: which part of the plugin has the duplicated name
    if duplicate_from == 'canonical':
        plugin = CategoryPlugin(Mock(category=duplicate_of),
                                aliases=['foo'])
    else:
        plugin = CategoryPlugin(Mock(category='foo'),
                                aliases=[duplicate_of])

    compilers = {'canonical': "FOO"}
    aliases = {'alias': 'canonical'}
    with patch.dict(COMPILER_LOC, compilers) as compilers_,\
            patch.dict(BASE + "_ALIASES", aliases) as aliases_:
        with pytest.raises(CategoryCompilerRegistrationError):
            _register_compiler_plugin(plugin)


@pytest.mark.parametrize('compiler_exists', [True, False])
def test_register_builder_plugin(compiler_exists, foo_baz_builder_plugin,
                                 foo_compiler):
    # _register_builder_plugin should register plugins that don't exist,
    # including registering the compiler if needed
    if compiler_exists:
        compilers = {'foo': foo_compiler}
    else:
        compilers = {}

    with patch.dict(COMPILER_LOC, compilers):
        if not compiler_exists:
            assert 'foo' not in _COMPILERS
        _register_builder_plugin(foo_baz_builder_plugin)
        assert 'foo' in _COMPILERS
        type_dispatch = _COMPILERS['foo'].type_dispatch
        assert type_dispatch['baz'] is foo_baz_builder_plugin
        assert type_dispatch['qux'] is foo_baz_builder_plugin


def test_register_plugins_unit(foo_compiler_plugin, foo_baz_builder_plugin):
    # register_plugins should correctly sort builder and compiler plugins,
    # and call the correct registration functions
    with patch(BASE + "_register_builder_plugin", Mock()) as builder, \
            patch(BASE + "_register_compiler_plugin", Mock()) as compiler:
        register_plugins([foo_baz_builder_plugin, foo_compiler_plugin])
        builder.assert_called_once_with(foo_baz_builder_plugin)
        compiler.assert_called_once_with(foo_compiler_plugin)


def test_register_plugins_integration(foo_compiler_plugin,
                                      foo_baz_builder_plugin):
    # register_plugins should correctly register plugins
    compilers = {}
    aliases = {}
    with patch.dict(COMPILER_LOC, compilers) as _compiler, \
                patch.dict(BASE + "_ALIASES", aliases) as _alias:
        assert 'foo' not in _COMPILERS
        register_plugins([foo_compiler_plugin, foo_baz_builder_plugin])
        assert 'foo' in _COMPILERS
        type_dispatch = _COMPILERS['foo'].type_dispatch
        assert type_dispatch['baz'] is foo_baz_builder_plugin


def test_sort_user_categories():
    # sorted user categories should match the expected compile order
    aliases = {'quux': 'qux'}
    # values for compilers and user_input shouldn't matter, but that's in
    # implementation detail that might change
    compilers = {'foo': "FOO", 'baz': "BAZ", 'bar': "BAR", 'qux': "QUX"}
    user_input = {'baz': "Baz", 'quux': "Qux", 'foo': "Foo", 'qux': "Qux"}
    order = ['foo', 'bar', 'baz', 'qux']
    expected = ['foo', 'baz', 'quux', 'qux']

    try:
        paths_cli.compiling.root_compiler.COMPILE_ORDER = order
        with patch.dict(COMPILER_LOC, compilers) as _compiler, \
                patch.dict(BASE + "_ALIASES", aliases) as _alias:
            assert _sort_user_categories(user_input) == expected
    finally:
        paths_cli.compiling.root_compiler.COMPILE_ORDER = COMPILE_ORDER
        # check that we unset properly (test the test)
        assert paths_cli.compiling.root_compiler.COMPILE_ORDER[0] == 'engine'


def test_do_compile():
    # compiler should correctly compile a basic input dict
    compilers = {
        'foo': CategoryCompiler({
            'baz': lambda dct: "BAZ" * dct['x']
        }, 'foo'),
        'bar': CategoryCompiler({
            'qux': lambda dct: "QUX" * dct['x']
        }, 'bar'),
    }
    aliases = {'baar': 'bar'}
    input_dict = {
        'foo': [{
            'type': 'baz',
            'x': 2
        }],
        'baar': [{
            'type': 'qux',
            'x': 3
        }]
    }
    order = ['bar', 'foo']
    try:
        paths_cli.compiling.root_compiler.COMPILE_ORDER = order
        with patch.dict(COMPILER_LOC, compilers) as _compiler,\
                patch.dict(BASE + "_ALIASES", aliases) as _alias:
            objs = do_compile(input_dict)
    finally:
        paths_cli.compiling.root_compiler.COMPILE_ORDER = COMPILE_ORDER
        # check that we unset properly (test the test)
        assert paths_cli.compiling.root_compiler.COMPILE_ORDER[0] == 'engine'

    assert objs == ["QUXQUXQUX", "BAZBAZ"]

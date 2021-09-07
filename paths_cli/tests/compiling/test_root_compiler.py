import pytest
import paths_cli
from paths_cli.compiling.root_compiler import *
from paths_cli.compiling.root_compiler import (
    _get_compiler, _get_registration_names, _register_builder_plugin,
    _register_compiler_plugin, _sort_user_categories, _CompilerProxy,
    _COMPILERS, _ALIASES
)
from unittest.mock import Mock, PropertyMock, patch
from paths_cli.compiling.core import Compiler, InstanceBuilder
from paths_cli.compiling.plugins import CompilerPlugin


### FIXTURES ###############################################################

@pytest.fixture
def foo_compiler():
    return Compiler(None, 'foo')

@pytest.fixture
def foo_compiler_plugin():
    return CompilerPlugin(Mock(compiler_name='foo'), ['bar'])

@pytest.fixture
def foo_baz_builder_plugin():
    builder = InstanceBuilder(None, [], name='baz')
    builder.compiler_name = 'foo'
    return builder

### CONSTANTS ##############################################################

COMPILER_LOC = "paths_cli.compiling.root_compiler._COMPILERS"
BASE = "paths_cli.compiling.root_compiler."

### TESTS ##################################################################

def clean_input_key():
    pytest.skip()

def test_canonical_name():
    pytest.skip()

class TestCompilerProxy:
    def setup(self):
        self.compiler = Compiler(None, "foo")
        self.compiler.named_objs['bar'] = 'baz'
        self.proxy = _CompilerProxy('foo')

    def test_proxy(self):
        # (NOT API) the _proxy should be the registered compiler
        with patch.dict(COMPILER_LOC, {'foo': self.compiler}):
            assert self.proxy._proxy is self.compiler

    def test_proxy_nonexisting(self):
        # _proxy should error if the no compiler is registered
        with pytest.raises(RuntimeError, match="No compiler registered"):
            self.proxy._proxy

    def test_named_objs(self):
        # the `.named_objs` attribute should work in the proxy
        with patch.dict(COMPILER_LOC, {'foo': self.compiler}):
            assert self.proxy.named_objs == {'bar': 'baz'}

    def test_call(self):
        # the `__call__` method should work in the proxy
        pytest.skip()

def test_compiler_for_nonexisting():
    # if nothing is ever registered with the compiler, then compiler_for
    # should error
    compilers = {}
    with patch.dict(COMPILER_LOC, compilers):
        assert 'foo' not in compilers
        proxy = compiler_for('foo')
        assert 'foo' not in compilers
        with pytest.raises(RuntimeError, match="No compiler registered"):
            proxy._proxy

def test_compiler_for_existing(foo_compiler):
    # if a compiler already exists when compiler_for is called, then
    # compiler_for should get that as its proxy
    with patch.dict(COMPILER_LOC, {'foo': foo_compiler}):
        proxy = compiler_for('foo')
        assert proxy._proxy is foo_compiler

def test_compiler_for_registered():
    # if a compiler is registered after compiler_for is called, then
    # compiler_for should use that as its proxy
    pytest.skip()

def test_compiler_for_registered_alias():
    # if compiler_for is registered as an alias, compiler_for should still
    # get the correct compiler
    pytest.skip()

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
    with patch.dict(COMPILER_LOC, compilers):
        assert 'foo' not in compilers
        _register_compiler_plugin(foo_compiler_plugin)
        assert 'foo' in _COMPILERS
        assert 'bar' in _ALIASES

    assert 'foo' not in _COMPILERS

def test_register_compiler_plugin_duplicate():
    # if a compiler of the same name exists either in canonical or aliases,
    # _register_compiler_plugin should raise an error
    pytest.skip()

def test_register_builder_plugin():
    # _register_builder_plugin should register plugins that don't exist,
    # including registering the compiler if needed
    pytest.skip()

def test_register_plugins_unit(foo_compiler_plugin, foo_baz_builder_plugin):
    # register_plugins should correctly sort builder and compiler plugins,
    # and call the correct registration functions
    with patch(BASE + "_register_builder_plugin", Mock()) as builder, \
            patch(BASE + "_register_compiler_plugin", Mock()) as compiler:
        register_plugins([foo_baz_builder_plugin, foo_compiler_plugin])
        assert builder.called_once_with(foo_baz_builder_plugin)
        assert compiler.called_once_with(foo_compiler_plugin)

def test_register_plugins_integration():
    # register_plugins should correctly register plugins
    pytest.skip()

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
    pytest.skip()
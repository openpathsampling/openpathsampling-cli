import pytest
import paths_cli
from paths_cli.parsing.root_parser import *
from paths_cli.parsing.root_parser import (
    _get_parser, _get_registration_names, _register_builder_plugin,
    _register_parser_plugin, _sort_user_categories, _ParserProxy, _PARSERS,
    _ALIASES
)
from unittest.mock import Mock, PropertyMock, patch
from paths_cli.parsing.core import Parser, InstanceBuilder
from paths_cli.parsing.plugins import ParserPlugin


### FIXTURES ###############################################################

@pytest.fixture
def foo_parser():
    return Parser(None, 'foo')

@pytest.fixture
def foo_parser_plugin():
    return ParserPlugin(Mock(parser_name='foo'), ['bar'])

@pytest.fixture
def foo_baz_builder_plugin():
    builder = InstanceBuilder(None, [], name='baz')
    builder.parser_name = 'foo'
    return builder

### CONSTANTS ##############################################################

PARSER_LOC = "paths_cli.parsing.root_parser._PARSERS"
BASE = "paths_cli.parsing.root_parser."

### TESTS ##################################################################

def clean_input_key():
    pytest.skip()

def test_canonical_name():
    pytest.skip()

class TestParserProxy:
    def setup(self):
        self.parser = Parser(None, "foo")
        self.parser.named_objs['bar'] = 'baz'
        self.proxy = _ParserProxy('foo')

    def test_proxy(self):
        # (NOT API) the _proxy should be the registered parser
        with patch.dict(PARSER_LOC, {'foo': self.parser}):
            assert self.proxy._proxy is self.parser

    def test_proxy_nonexisting(self):
        # _proxy should error if the no parser is registered
        with pytest.raises(RuntimeError, match="No parser registered"):
            self.proxy._proxy

    def test_named_objs(self):
        # the `.named_objs` attribute should work in the proxy
        with patch.dict(PARSER_LOC, {'foo': self.parser}):
            assert self.proxy.named_objs == {'bar': 'baz'}

    def test_call(self):
        # the `__call__` method should work in the proxy
        pytest.skip()

def test_parser_for_nonexisting():
    # if nothing is ever registered with the parser, then parser_for should
    # error
    parsers = {}
    with patch.dict(PARSER_LOC, parsers):
        assert 'foo' not in parsers
        proxy = parser_for('foo')
        assert 'foo' not in parsers
        with pytest.raises(RuntimeError, match="No parser registered"):
            proxy._proxy

def test_parser_for_existing(foo_parser):
    # if a parser already exists when parser_for is called, then parser_for
    # should get that as its proxy
    with patch.dict(PARSER_LOC, {'foo': foo_parser}):
        proxy = parser_for('foo')
        assert proxy._proxy is foo_parser

def test_parser_for_registered():
    # if a parser is registered after parser_for is called, then parser_for
    # should use that as its proxy
    pytest.skip()

def test_parser_for_registered_alias():
    # if parser_for is registered as an alias, parser_for should still get
    # the correct parser
    pytest.skip()

def test_get_parser_existing(foo_parser):
    # if a parser has been registered, then _get_parser should return the
    # registered parser
    with patch.dict(PARSER_LOC, {'foo': foo_parser}):
        assert _get_parser('foo') is foo_parser

def test_get_parser_nonexisting(foo_parser):
    # if a parser has not been registered, then _get_parser should create
    # the parser
    with patch.dict(PARSER_LOC, {}):
        parser = _get_parser('foo')
        assert parser is not foo_parser  # overkill
        assert parser.label == 'foo'
        assert 'foo' in _PARSERS

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

def test_register_parser_plugin(foo_parser_plugin):
    # _register_parser_plugin should register parsers that don't exist
    parsers = {}
    with patch.dict(PARSER_LOC, parsers):
        assert 'foo' not in parsers
        _register_parser_plugin(foo_parser_plugin)
        assert 'foo' in _PARSERS
        assert 'bar' in _ALIASES

    assert 'foo' not in _PARSERS

def test_register_parser_plugin_duplicate():
    # if a parser of the same name exists either in canonical or aliases,
    # _register_parser_plugin should raise an error
    pytest.skip()

def test_register_builder_plugin():
    # _register_builder_plugin should register plugins that don't exist,
    # including registering the parser if needed
    pytest.skip()

def test_register_plugins_unit(foo_parser_plugin, foo_baz_builder_plugin):
    # register_plugins should correctly sort builder and parser plugins, and
    # call the correct registration functions
    with patch(BASE + "_register_builder_plugin", Mock()) as builder, \
            patch(BASE + "_register_parser_plugin", Mock()) as parser:
        register_plugins([foo_baz_builder_plugin, foo_parser_plugin])
        assert builder.called_once_with(foo_baz_builder_plugin)
        assert parser.called_once_with(foo_parser_plugin)

def test_register_plugins_integration():
    # register_plugins should correctly register plugins
    pytest.skip()

def test_sort_user_categories():
    # sorted user categories should match the expected parse order
    aliases = {'quux': 'qux'}
    # values for parsers and user_input shouldn't matter, but that's in
    # implementation detail that might change
    parsers = {'foo': "FOO", 'baz': "BAZ", 'bar': "BAR", 'qux': "QUX"}
    user_input = {'baz': "Baz", 'quux': "Qux", 'foo': "Foo", 'qux': "Qux"}
    order = ['foo', 'bar', 'baz', 'qux']
    expected = ['foo', 'baz', 'quux', 'qux']

    try:
        paths_cli.parsing.root_parser.PARSE_ORDER = order
        with patch.dict(PARSER_LOC, parsers) as _parser, \
                patch.dict(BASE + "_ALIASES", aliases) as _alias:
            assert _sort_user_categories(user_input) == expected
    finally:
        paths_cli.parsing.root_parser.PARSE_ORDER = PARSE_ORDER
        # check that we unset properly (test the test)
        assert paths_cli.parsing.root_parser.PARSE_ORDER[0] == 'engine'

def test_parse():
    # parser should correctly parse a basic input dict
    pytest.skip()

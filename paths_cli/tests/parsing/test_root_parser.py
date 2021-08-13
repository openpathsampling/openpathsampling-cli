import pytest
from paths_cli.parsing.root_parser import *
from paths_cli.parsing.root_parser import (
    _get_parser, _get_registration_names, _register_builder_plugin,
    _register_parser_plugin
)
from unittest.mock import Mock, patch
from paths_cli.parsing.core import Parser

PARSER_LOC = "paths_cli.parsing.root_parser.PARSERS"

class TestParserProxy:
    def setup(self):
        self.parser = Parser(None, "foo")
        self.parser.named_objs['bar'] = 'baz'
        self.proxy = ParserProxy('foo')
        pass

    def test_proxy(self):
        # (NOT API) the _proxy should be the registered parser
        with patch.dict(PARSER_LOC, {'foo': self.parser}):
            assert self.proxy._proxy is self.parser

    def test_proxy_nonexisting(self):
        # _proxy should error if the no parser is registered
        with pytest.raises(KeyError):
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
        with pytest.raises(KeyError):
            proxy._proxy

def test_parser_for_existing():
    # if a parser already exists when parser_for is called, then parser_for
    # should get that as its proxy
    foo_parser = Parser(None, 'foo')
    with patch.dict(PARSER_LOC, {'foo': foo_parser}):
        proxy = parser_for('foo')
        assert proxy._proxy is foo_parser

def test_parser_for_registered():
    # if a parser is registered after parser_for is called, then parser_for
    # should use that as its proxy
    pytest.skip()

def test_get_parser_existing():
    # if a parser has been registered, then _get_parser should return the
    # registered parser
    pytest.skip()

def test_get_parser_nonexisting():
    # if a parser has not been registered, then _get_parser should create
    # the parser
    pytest.skip()

def test_get_registration_names():
    # _get_registration_names should always provide the names in order
    # `canonical, alias1, alias2, ...` regardless of whether `canonical` is
    # also listed in the aliases
    pytest.skip()

def test_register_parser_plugin():
    # _register_parser_plugin should register parsers that don't exist
    pytest.skip()

def test_register_parser_plugin_duplicate():
    # if a parser of the same name exists either in canonical or aliases,
    # _register_parser_plugin should raise an error
    pytest.skip()

def test_register_builder_plugin():
    # _register_builder_plugin should register plugins that don't exist,
    # including registering the parser if needed
    pytest.skip()

def test_register_plugins_unit():
    # register_plugins should correctly sort builder and parser plugins, and
    # call the correct registration functions
    # TODO: patch _register_builder & _register_parser; this is unit, not
    # integration
    pytest.skip()

def test_register_plugins_integration():
    # register_plugins should correctly register plugins
    pytest.skip()

def test_parse():
    # parser should correctly parse a basic input dict
    pytest.skip()

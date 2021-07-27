import pytest
from unittest import mock

from openpathsampling.experimental.storage.collective_variables import \
        CoordinateFunctionCV

from paths_cli.wizard.core import *

from paths_cli.tests.wizard.mock_wizard import (
    make_mock_wizard, make_mock_retry_wizard
)

@pytest.mark.parametrize('req,expected', [
    (('foo', 2, 2), '2'), (('foo', 2, float('inf')), 'at least 2'),
    (('foo', 0, 2), 'at most 2'),
    (('foo', 1, 3), 'at least 1 and at most 3')
])
def test_interpret_req(req, expected):
    assert interpret_req(req) == expected

@pytest.mark.parametrize('length,expected', [
    (0, 'foo'), (1, 'baz'), (2, 'quux'),
])
def test_get_missing_object(length, expected):
    dct = dict([('bar', 'baz'), ('qux', 'quux')][:length])
    fallback = lambda x: 'foo'
    wizard = make_mock_wizard('2')
    result = get_missing_object(wizard, dct, display_name='string',
                                fallback_func=fallback)
    assert result == expected

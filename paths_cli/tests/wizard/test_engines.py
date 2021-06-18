import pytest
from unittest import mock

from paths_cli.tests.wizard.mock_wizard import mock_wizard

from paths_cli.wizard.engines import engines, SUPPORTED_ENGINES

def test_engines():
    wizard = mock_wizard(['foo'])
    with mock.patch.dict(SUPPORTED_ENGINES,
                         {'foo': mock.Mock(return_value='ran foo')}):
        foo = engines(wizard)
    assert foo == 'ran foo'


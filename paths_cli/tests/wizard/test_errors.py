import pytest
from unittest import mock

from paths_cli.tests.wizard.mock_wizard import mock_wizard

from paths_cli.wizard.errors import *

def test_impossible_error_default():
    with pytest.raises(ImpossibleError, match="You should never see this."):
        raise ImpossibleError()

@pytest.mark.parametrize('inputs', ['r', 'q'])
def test_not_installed(inputs):
    expected = {'r': RestartObjectException, 'q': SystemExit}[inputs]
    wizard = mock_wizard([inputs])
    with pytest.raises(expected):
        not_installed(wizard, 'foo', 'widget')
    log = wizard.console.log_text
    assert 'foo installed' in log
    assert 'different widget' in log


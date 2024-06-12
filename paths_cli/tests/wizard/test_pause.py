import pytest
import time
from paths_cli.tests.wizard.mock_wizard import mock_wizard

from paths_cli.wizard.pause import *

@pytest.fixture(autouse=True, scope="module")
def use_default_pause_style():
    with pause_style('default'):
        yield


def test_get_pause_style():
    default_style = PAUSE_STYLES['default']
    assert get_pause_style() == default_style


@pytest.mark.parametrize('input_type', ['string', 'tuple', 'PauseStyle'])
def test_set_pause_style(input_type):
    # check that we have the default settings
    default_style = PAUSE_STYLES['default']
    test_style = PAUSE_STYLES['testing']
    input_val = {
        'string': 'testing',
        'tuple': tuple(test_style),
        'PauseStyle': PauseStyle(*test_style)
    }[input_type]
    assert input_val is not test_style  # always a different object
    assert get_pause_style() == default_style
    set_pause_style(input_val)
    assert get_pause_style() != default_style
    assert get_pause_style() == test_style
    set_pause_style('default')  # explicitly reset default


def test_set_pause_bad_name():
    with pytest.raises(RuntimeError, match="Unknown pause style"):
        set_pause_style('foo')

    # ensure we didn't break anything for later tests
    assert get_pause_style() == PAUSE_STYLES['default']


def test_pause_style_context():
    assert get_pause_style() == PAUSE_STYLES['default']
    with pause_style('testing'):
        assert get_pause_style() == PAUSE_STYLES['testing']
    assert get_pause_style() == PAUSE_STYLES['default']


def _run_pause_test(func):
    test_style = PAUSE_STYLES['testing']
    expected = getattr(test_style, func.__name__)
    wiz = mock_wizard([])
    with pause_style(test_style):
        start = time.time()
        func(wiz)
        duration = time.time() - start
    assert expected <= duration < 1.1 * duration
    return wiz


def test_short():
    _ = _run_pause_test(short)


def test_long():
    _ = _run_pause_test(long)


def test_section():
    wiz = _run_pause_test(section)

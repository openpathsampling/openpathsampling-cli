import pytest
from unittest import mock

from paths_cli.tests.wizard.mock_wizard import mock_wizard

from paths_cli.wizard.volumes import (
    _vol_intro, intersection_volume, union_volume, negated_volume,
    cv_defined_volume, volumes, SUPPORTED_VOLUMES
)

import openpathsampling as paths
from openpathsampling.experimental.storage.collective_variables import \
        CoordinateFunctionCV

from openpathsampling.tests.test_helpers import make_1d_traj

def _wrap(x, period_min, period_max):
    # used in testing periodic CVs
    while x >= period_max:
        x -= period_max - period_min
    while x < period_min:
        x += period_max - period-min
    return x


@pytest.fixture
def volume_setup():
    cv = CoordinateFunctionCV(lambda snap: snap.xyz[0][0]).named('x')
    vol1 = paths.CVDefinedVolume(cv, 0.0, 1.0)
    vol2 = paths.CVDefinedVolume(cv, 0.5, 1.5)
    return vol1, vol2

@pytest.mark.parametrize('as_state,has_state', [
    (True, False), (True, True), (False, False)
])
def test_vol_intro(as_state, has_state):
    wizard = mock_wizard([])
    wizard.requirements['state'] = ('states', 2, float('inf'))
    if has_state:
        wizard.states['foo'] = 'placeholder'

    intro = _vol_intro(wizard, as_state)

    if as_state and has_state:
        assert "another stable state" in intro
    elif as_state and not has_state:
        assert "You'll need to define" in intro
    elif not as_state:
        assert intro is None
    else:
        raise RuntimeError("WTF?")

def _binary_volume_test(volume_setup, func):
    vol1, vol2 = volume_setup
    wizard = mock_wizard([])
    mock_volumes = mock.Mock(side_effect=[vol1, vol2])
    with mock.patch('paths_cli.wizard.volumes.volumes', new=mock_volumes):
        vol = func(wizard)

    assert "first volume" in wizard.console.log_text
    assert "second volume" in wizard.console.log_text
    assert "Created" in wizard.console.log_text
    return wizard, vol

def test_intersection_volume(volume_setup):
    wizard, vol = _binary_volume_test(volume_setup, intersection_volume)
    assert "intersection" in wizard.console.log_text
    traj = make_1d_traj([0.25, 0.75])
    assert not vol(traj[0])
    assert vol(traj[1])

def test_union_volume(volume_setup):
    wizard, vol = _binary_volume_test(volume_setup, union_volume)
    assert "union" in wizard.console.log_text
    traj = make_1d_traj([0.25, 0.75, 1.75])
    assert vol(traj[0])
    assert vol(traj[1])
    assert not vol(traj[2])

def test_negated_volume(volume_setup):
    init_vol, _ = volume_setup
    traj = make_1d_traj([0.5, 1.5])
    assert init_vol(traj[0])
    assert not init_vol(traj[1])
    wizard = mock_wizard([])
    mock_vol = mock.Mock(return_value=init_vol)
    with mock.patch('paths_cli.wizard.volumes.volumes', new=mock_vol):
        vol = negated_volume(wizard)

    assert "not in" in wizard.console.log_text
    assert not vol(traj[0])
    assert vol(traj[1])

@pytest.mark.parametrize('periodic', [True, False])
def test_cv_defined_volume(periodic):
    if periodic:
        min_ = 0.0
        max_ = 1.0
        cv = CoordinateFunctionCV(
            lambda snap: _wrap(snap.xyz[0][0], period_min=min_,
                               period_max=max_),
            period_min=min_, period_max=max_
        ).named('x')
        inputs = ['x', '0.75', '1.25']
        in_state = make_1d_traj([0.2, 0.8])
        out_state = make_1d_traj([0.5])
    else:
        cv = CoordinateFunctionCV(lambda snap: snap.xyz[0][0]).named('x')
        inputs = ['x', '0.0', '1.0']
        in_state = make_1d_traj([0.5])
        out_state = make_1d_traj([-0.1, 1.1])
    wizard = mock_wizard(inputs)
    wizard.cvs[cv.name] = cv
    vol = cv_defined_volume(wizard)
    assert "interval" in wizard.console.log_text
    for snap in in_state:
        assert vol(snap)
    for snap in out_state:
        assert not vol(snap)

@pytest.mark.parametrize('intro', [None, "", "foo"])
def test_volumes(intro):
    say_hello = mock.Mock(return_value="hello!")
    wizard = mock_wizard(['Hello world'])
    with mock.patch.dict(SUPPORTED_VOLUMES, {'Hello world': say_hello}):
        assert volumes(wizard, intro=intro) == "hello!"
        assert wizard.console.input_call_count == 1


    n_statements = 2 * (1 + 3)
    # 2: line and blank; (1 + 3): 1 in volumes + 3 in ask_enumerate

    if intro == 'foo':
        assert 'foo' in wizard.console.log_text
        assert len(wizard.console.log) == n_statements + 2  # from intro
    else:
        assert 'foo' not in wizard.console.log_text
        assert len(wizard.console.log) == n_statements

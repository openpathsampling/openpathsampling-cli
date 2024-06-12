import pytest
from unittest import mock

from paths_cli.tests.wizard.mock_wizard import mock_wizard

from paths_cli.wizard.volumes import (
    INTERSECTION_VOLUME_PLUGIN, UNION_VOLUME_PLUGIN, NEGATED_VOLUME_PLUGIN,
    CV_DEFINED_VOLUME_PLUGIN, volume_intro, _VOL_DESC,
    volume_ask
)

import openpathsampling as paths
from openpathsampling.experimental.storage.collective_variables import \
        CoordinateFunctionCV

from openpathsampling.tests.test_helpers import make_1d_traj


@pytest.fixture
def volume_setup():
    cv = CoordinateFunctionCV(lambda snap: snap.xyz[0][0]).named('x')
    vol1 = paths.CVDefinedVolume(cv, 0.0, 1.0)
    vol2 = paths.CVDefinedVolume(cv, 0.5, 1.5)
    return vol1, vol2

@pytest.mark.parametrize('as_state,has_state', [
    (True, False), (True, True), (False, False)
])
def test_volume_intro(as_state, has_state):
    wizard = mock_wizard([])
    wizard.requirements['state'] = ('states', 2, float('inf'))
    if has_state:
        wizard.states['foo'] = 'placeholder'

    if as_state:
        context = {}
    else:
        context = {'depth': 1}

    intro = "\n".join(volume_intro(wizard, context))

    if as_state and has_state:
        assert "another stable state" in intro
    elif as_state and not has_state:
        assert "You'll need to define" in intro
    elif not as_state:
        assert intro == _VOL_DESC
    else:  # -no-cov-
        raise RuntimeError("WTF?")

def _binary_volume_test(volume_setup, func):
    vol1, vol2 = volume_setup
    wizard = mock_wizard([])
    mock_volumes = mock.Mock(side_effect=[vol1, vol2])
    patch_loc = 'paths_cli.wizard.volumes.VOLUMES_PLUGIN'
    with mock.patch(patch_loc, new=mock_volumes):
        vol = func(wizard)

    assert "first constituent volume" in wizard.console.log_text
    assert "second constituent volume" in wizard.console.log_text
    assert "Here's what we'll make" in wizard.console.log_text
    return wizard, vol

def test_intersection_volume(volume_setup):
    wizard, vol = _binary_volume_test(volume_setup,
                                      INTERSECTION_VOLUME_PLUGIN)
    assert "intersection" in wizard.console.log_text
    traj = make_1d_traj([0.25, 0.75])
    assert not vol(traj[0])
    assert vol(traj[1])

def test_union_volume(volume_setup):
    wizard, vol = _binary_volume_test(volume_setup, UNION_VOLUME_PLUGIN)
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
    patch_loc = 'paths_cli.wizard.volumes.VOLUMES_PLUGIN'
    with mock.patch(patch_loc, new=mock_vol):
        vol = NEGATED_VOLUME_PLUGIN(wizard)

    assert "not in" in wizard.console.log_text
    assert not vol(traj[0])
    assert vol(traj[1])

@pytest.mark.parametrize('depth', [0, 1, None])
def test_volume_ask(depth):
    context = {0: {'depth': 0},
               1: {'depth': 1},
               None: {}}[depth]
    wiz = mock_wizard([])
    result = volume_ask(wiz, context)
    if depth == 1:
        assert result == "What describes this volume?"
    else:
        assert result == "What describes this state?"


@pytest.mark.parametrize('periodic', [True, False])
def test_cv_defined_volume(periodic):
    if periodic:
        min_ = 0.0
        max_ = 1.0
        cv = CoordinateFunctionCV(
            lambda snap: snap.xyz[0][0],
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
    vol = CV_DEFINED_VOLUME_PLUGIN(wizard)
    assert "interval" in wizard.console.log_text
    for snap in in_state:
        assert vol(snap)
    for snap in out_state:
        assert not vol(snap)

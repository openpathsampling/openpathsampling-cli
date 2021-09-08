import pytest

from paths_cli.compiling.schemes import *
import openpathsampling as paths

from unittest.mock import patch
from openpathsampling.tests.test_helpers import make_1d_traj
from paths_cli.tests.compiling.utils import mock_compiler
from paths_cli.compiling.strategies import ONE_WAY_SHOOTING_STRATEGY_PLUGIN

_COMPILERS_LOC = 'paths_cli.compiling.root_compiler._COMPILERS'

@pytest.fixture
def tps_compilers_and_traj(tps_network_and_traj, flat_engine):
    network, traj = tps_network_and_traj
    compilers = {
        'network': mock_compiler('network', None, {'tps_network': network}),
        'engine': mock_compiler('engine', None,
                                {'flat_engine': flat_engine}),
    }
    return compilers, traj

@pytest.fixture
def tis_compilers_and_traj(tps_network_and_traj, tis_network, flat_engine):
    _, traj = tps_network_and_traj
    compilers = {
        'network': mock_compiler('network', None,
                                 {'tis_network': tis_network}),
        'engine': mock_compiler('engine', None,
                                {'flat_engine': flat_engine}),
    }
    return compilers, traj

def test_build_spring_shooting_scheme(tps_compilers_and_traj):
    paths.InterfaceSet._reset()

    compilers, traj = tps_compilers_and_traj
    dct = {'network': 'tps_network', 'k_spring': 0.5, 'delta_max': 100,
           'engine': 'flat_engine'}
    with patch.dict(_COMPILERS_LOC, compilers):
        scheme = SPRING_SHOOTING_PLUGIN(dct)

    assert isinstance(scheme, paths.SpringShootingMoveScheme)
    # smoke test that it can build its tree and load init conds
    scheme.move_decision_tree()
    assert len(scheme.strategies) == 2  # includes the global
    _ = scheme.initial_conditions_from_trajectories(traj)


@pytest.mark.parametrize('network', ['tps', 'tis'])
def test_build_one_way_shooting_scheme(network, tps_compilers_and_traj,
                                       tis_compilers_and_traj):
    paths.InterfaceSet._reset()
    compilers, traj = {'tps': tps_compilers_and_traj,
                       'tis': tis_compilers_and_traj}[network]
    dct = {'network': f"{network}_network", 'engine': 'flat_engine'}
    with patch.dict(_COMPILERS_LOC, compilers):
        scheme = ONE_WAY_SHOOTING_SCHEME_PLUGIN(dct)

    assert isinstance(scheme, paths.OneWayShootingMoveScheme)
    # smoke test that it can build its tree and load init conds
    scheme.move_decision_tree()
    _ = scheme.initial_conditions_from_trajectories(traj)


def test_movescheme_plugin(tis_compilers_and_traj):
    paths.InterfaceSet._reset()
    compilers, traj = tis_compilers_and_traj
    compilers['strategy'] = mock_compiler(
        'strategy',
        type_dispatch={
            'one-way-shooting': ONE_WAY_SHOOTING_STRATEGY_PLUGIN
        },
        named_objs={}
    )

    dct = {'network': 'tis_network',
           'strategies': [
               {'type': 'one-way-shooting',
                'engine': 'flat_engine'},
           ]}
    with patch.dict(_COMPILERS_LOC, compilers):
        scheme = MOVESCHEME_PLUGIN(dct)

    assert isinstance(scheme, paths.MoveScheme)
    # smoke test that it can build its tree and load init conds
    scheme.move_decision_tree()
    _ = scheme.initial_conditions_from_trajectories(traj)

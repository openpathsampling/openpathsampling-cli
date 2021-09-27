from openpathsampling.tests.test_helpers import make_1d_traj
from openpathsampling.engines import toy as toys
import openpathsampling as paths
import pytest

import pathlib

@pytest.fixture
def test_data_dir():
    tests = pathlib.Path(__file__).parent / "testdata"
    return tests


@pytest.fixture
def flat_engine():
    pes = toys.LinearSlope([0, 0, 0], 0)
    topology = toys.Topology(n_spatial=3, masses=[1.0, 1.0, 1.0], pes=pes)
    integ = toys.LeapfrogVerletIntegrator(dt=0.1)
    options = {'integ': integ,
               'n_frames_max': 1000,
               'n_steps_per_frame': 1}
    engine = toys.Engine(options=options, topology=topology).named("flat")
    return engine

@pytest.fixture
def cv_and_states():
    cv = paths.CoordinateFunctionCV("x", lambda s: s.xyz[0][0])
    state_A = paths.CVDefinedVolume(cv, float("-inf"), 0).named("A")
    state_B = paths.CVDefinedVolume(cv, 1, float("inf")).named("B")
    return cv, state_A, state_B

@pytest.fixture
def transition_traj():
    init_traj = make_1d_traj([-0.1, 0.1, 0.3, 0.5, 0.7, 0.9, 1.1],
                             [2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0])
    return init_traj

@pytest.fixture
def tps_network_and_traj(cv_and_states, transition_traj):
    _, state_A, state_B = cv_and_states
    network = paths.TPSNetwork(state_A, state_B)
    return network, transition_traj

@pytest.fixture
def tps_fixture(flat_engine, tps_network_and_traj):
    network, traj = tps_network_and_traj
    scheme = paths.OneWayShootingMoveScheme(network=network,
                                            selector=paths.UniformSelector(),
                                            engine=flat_engine)
    init_conds = scheme.initial_conditions_from_trajectories(traj)
    return (scheme, network, flat_engine, init_conds)


@pytest.fixture
def tis_network(cv_and_states):
    cv, state_A, state_B = cv_and_states
    interfaces = paths.VolumeInterfaceSet(cv, float("-inf"),
                                          [0.0, 0.1, 0.2])
    network = paths.MISTISNetwork([(state_A, interfaces, state_B)])
    return network

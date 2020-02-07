from openpathsampling.tests.test_helpers import make_1d_traj
from openpathsampling.engines import toy as toys
import openpathsampling as paths
import pytest

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
def tps_network_and_traj():
    cv = paths.CoordinateFunctionCV("x", lambda s: s.xyz[0][0])
    state_A = paths.CVDefinedVolume(cv, float("-inf"), 0).named("A")
    state_B = paths.CVDefinedVolume(cv, 1, float("inf")).named("B")
    network = paths.TPSNetwork(state_A, state_B)
    init_traj = make_1d_traj([-0.1, 0.1, 0.3, 0.5, 0.7, 0.9, 1.1],
                             [2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0])
    return (network, init_traj)

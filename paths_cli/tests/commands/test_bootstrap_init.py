import pytest
from click.testing import CliRunner
from unittest.mock import patch
import numpy as np

from paths_cli.commands.bootstrap_init import *
import openpathsampling as paths
from openpathsampling.engines import toy
from openpathsampling.tests.test_helpers import make_1d_traj

@pytest.fixture
def toy_2_state_engine():
    pes = (
        toy.OuterWalls([1.0, 1.0], [0.0, 0.0]) +
        toy.Gaussian(-1.0, [12.0, 12.0], [-0.5, 0.0]) +
        toy.Gaussian(-1.0, [12.0, 12.0], [0.5, 0.0])
    )
    topology=toy.Topology(
        n_spatial = 2,
        masses =[1.0, 1.0],
        pes = pes
    )
    integ = toy.LangevinBAOABIntegrator(dt=0.02, temperature=0.1, gamma=2.5)
    options = {
        'integ': integ,
        'n_frames_max': 5000,
        'n_steps_per_frame': 1
    }

    engine = toy.Engine(
        options=options,
        topology=topology
    )
    return engine

@pytest.fixture
def toy_2_state_cv():
    return paths.FunctionCV("x", lambda s: s.xyz[0][0])

@pytest.fixture
def toy_2_state_volumes(toy_2_state_cv):
    state_A = paths.CVDefinedVolume(
        toy_2_state_cv,
        float("-inf"),
        -0.3,
    ).named("A")
    state_B = paths.CVDefinedVolume(
        toy_2_state_cv,
        0.3,
        float("inf"),
    ).named("B")
    return state_A, state_B

@pytest.fixture
def toy_2_state_tis(toy_2_state_cv, toy_2_state_volumes):
    state_A, state_B = toy_2_state_volumes
    interfaces = paths.VolumeInterfaceSet(
        toy_2_state_cv,
        float("-inf"),
        [-0.3, -0.2, -0.1],
    )
    tis = paths.MISTISNetwork(
        [(state_A, interfaces, state_B)],
    )
    return tis


def print_test(init_frame, network, engine, transition, output_storage):
    print(init_frame.__uuid__)
    print(network.__uuid__)
    print(engine.__uuid__)
    # apparently transition UUID isn't preserved, but these are?
    print(transition.stateA.__uuid__)
    print(transition.stateB.__uuid__)
    print([e.__uuid__ for e in transition.ensembles])
    print(isinstance(output_storage, paths.Storage))

@patch('paths_cli.commands.bootstrap_init.bootstrap_init_main', print_test)
def test_bootstrap_init(tis_fixture):
    scheme, network, engine, init_conds = tis_fixture
    runner = CliRunner()
    with runner.isolated_filesystem():
        storage = paths.Storage("setup.nc", 'w')
        storage.save(init_conds)
        for obj in tis_fixture:
            storage.save(obj)

        storage.tags["init_snap"] = init_conds[0][0]
        storage.close()

        results = runner.invoke(bootstrap_init, [
            'setup.nc',
            '-o', 'foo.nc',
            '--initial-state', "A",
            '--final-state', "B",
            '--init-frame', 'init_snap',
        ])

        transitions = list(network.transitions.values())
        assert len(transitions) == 1
        transition = transitions[0]
        stateA = transition.stateA
        stateB = transition.stateB
        ensembles = transition.ensembles

        expected_output = (
            f"{init_conds[0][0].__uuid__}\n{network.__uuid__}\n"
            f"{engine.__uuid__}\n"
            f"{stateA.__uuid__}\n{stateB.__uuid__}\n"
            f"{[e.__uuid__ for e in ensembles]}\n"
            "True\n"
        )
        assert results.exit_code == 0
        assert results.output == expected_output


def test_bootstrap_init_main(toy_2_state_tis, toy_2_state_engine, tmp_path):
    network = toy_2_state_tis
    engine = toy_2_state_engine
    scheme = paths.DefaultScheme(network, engine)
    init_frame = toy.Snapshot(
        coordinates=np.array([[-0.5, -0.5]]),
        velocities=np.array([[0.0,0.0]]),
        engine=engine
    )
    assert len(network.transitions) == 1
    transition = list(network.transitions.values())[0]
    output_storage = paths.Storage(tmp_path / "output.nc", mode='w')
    init_conds, bootstrapper = bootstrap_init_main(init_frame, network,
                                                   engine, transition,
                                                   output_storage)
    init_conds.sanity_check()

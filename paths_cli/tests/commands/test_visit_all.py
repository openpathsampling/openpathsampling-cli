import os

import pytest
from unittest.mock import patch, MagicMock
import tempfile
from click.testing import CliRunner

from paths_cli.commands.visit_all import *

import openpathsampling as paths

# patch with this for testing
def print_test(output_storage, states, engine, initial_frame):
    print(isinstance(output_storage, paths.Storage))
    print(sorted([s.__uuid__ for s in states]))
    print(engine.__uuid__)
    print(initial_frame.__uuid__)


@pytest.fixture()
def tps_fixture(flat_engine, tps_network_and_traj):
    network, traj = tps_network_and_traj
    scheme = paths.OneWayShootingMoveScheme(network=network,
                                            selector=paths.UniformSelector(),
                                            engine=flat_engine)
    init_conds = scheme.initial_conditions_from_trajectories(traj)
    return (scheme, network, flat_engine, init_conds)

@pytest.fixture()
def visit_all_fixture(tps_fixture):
    scheme, network, engine, init_conds = tps_fixture
    states = sorted(network.all_states, key=lambda x: x.__uuid__)
    init_frame = init_conds[0].trajectory[0]
    return states, engine, init_frame


@patch('paths_cli.commands.visit_all.visit_all_main', print_test)
def test_visit_all(visit_all_fixture):
    # this is an integration test; testing integration click & parameters
    states, engine, init_frame = visit_all_fixture
    runner = CliRunner()
    with runner.isolated_filesystem():
        storage = paths.Storage("setup.nc", 'w')
        for obj in visit_all_fixture:
            storage.save(obj)
        storage.tags['initial_snapshot'] = init_frame
        storage.close()

        results = runner.invoke(
            visit_all,
            ["setup.nc", '-o', 'foo.nc', '-s', 'A', '-s', 'B',
             '-e', 'flat', '-f', 'initial_snapshot']
        )

    expected_output = ("True\n[" + str(states[0].__uuid__) + ", "
                       + str(states[1].__uuid__) + "]\n")
    expected_output += "\n".join(str(obj.__uuid__)
                                 for obj in [engine, init_frame]) + "\n"
    assert results.exit_code == 0
    assert results.output == expected_output

def test_visit_all_main(visit_all_fixture):
    # just a smoke test here
    tempdir = tempfile.mkdtemp()
    try:
        store_name = os.path.join(tempdir, "visit_all.nc")
        storage = paths.Storage(store_name, mode='w')
        states, engine, init_frame = visit_all_fixture
        traj, foo = visit_all_main(storage, states, engine, init_frame)
        assert isinstance(traj, paths.Trajectory)
        assert foo is None
        assert len(storage.trajectories) == 1
        storage.close()
    finally:
        os.remove(store_name)
        os.rmdir(tempdir)

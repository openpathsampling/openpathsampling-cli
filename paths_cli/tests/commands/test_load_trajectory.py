from click.testing import CliRunner
from contextlib import contextmanager
import pytest
from importlib import resources
from openpathsampling.tests.test_helpers import data_filename
import openpathsampling as paths

from paths_cli.commands.load_trajectory import *


@contextmanager
def run_load_trajectory(args):
    runner = CliRunner()
    with runner.isolated_filesystem():
        storage = paths.Storage("setup.nc", 'w')
        storage.close()
        results = runner.invoke(
            load_trajectory,
            args
        )
        assert results.exit_code == 0
        st = paths.Storage("setup.nc", mode='r')
        assert len(st.trajectories) == 1
        yield st


@pytest.mark.parametrize("with_top", [True, False])
@pytest.mark.parametrize("with_tag", [True, False])
def test_load_trajectory_pdb(with_top, with_tag):
    # test that we can load a PDB file with or without topology; also tests
    # that the taging works correctly
    pdb_path = data_filename("ala_small_traj.pdb")
    out_file = "setup.nc"
    args = [
        pdb_path,
        '--append-file', out_file,
    ]
    if with_top:
        args.extend(['--top', pdb_path])

    if with_tag:
        args.extend(['--tag', 'init_snap'])

    with run_load_trajectory(args) as st:
        traj = st.trajectories[0]
        assert len(traj) == 10
        if with_tag:
            tagged = st.tags['init_snap']
            assert tagged == traj

def test_load_trajectory_trr():
    trr = data_filename("gromacs_engine/project_trr/0000000.trr")
    gro = data_filename("gromacs_engine/conf.gro")
    out_file = "setup.nc"
    args = [
        trr,
        '--append-file', out_file,
        '--top', gro,
    ]
    with run_load_trajectory(args) as st:
        traj = st.trajectories[0]
        assert len(traj) == 4

def test_load_trajectory_bad_topology():
    trr = data_filename("gromacs_engine/project_trr/0000000.trr")
    pdb = data_filename("tip4p_water.pdb")
    out_file = "setup.nc"
    args = [
        trr,
        '--append-file', out_file,
        '--top', pdb,
    ]
    runner = CliRunner()
    with runner.isolated_filesystem():
        storage = paths.Storage("setup.nc", 'w')
        storage.close()
        result = runner.invoke(
            load_trajectory,
            args
        )
        assert result.exit_code == 1
        assert "topology" in str(result.exception)
        assert "same atoms" in str(result.exception)

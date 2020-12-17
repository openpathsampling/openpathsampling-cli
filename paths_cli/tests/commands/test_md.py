import pytest
import os
import tempfile
from unittest.mock import patch, Mock
from click.testing import CliRunner

from paths_cli.commands.md import *

import openpathsampling as paths

from openpathsampling.tests.test_helpers import \
        make_1d_traj, CalvinistDynamics

class TestProgressReporter(object):
    def setup(self):
        self.progress = ProgressReporter(timestep=None, update_freq=5)

    @pytest.mark.parametrize('timestep', [None, 0.1])
    def test_progress_string(self, timestep):
        progress = ProgressReporter(timestep, update_freq=5)
        expected = "Ran 25 frames"
        if timestep is not None:
            expected += " [2.5]"
        expected += '.\n'
        assert progress.progress_string(25) == expected

    @pytest.mark.parametrize('n_steps', [0, 5, 6])
    @pytest.mark.parametrize('force', [True, False])
    @patch('openpathsampling.tools.refresh_output',
           lambda s: print(s, end=''))
    def test_report_progress(self, n_steps, force, capsys):
        self.progress.report_progress(n_steps, force)
        expected = "Ran {n_steps} frames.\n".format(n_steps=n_steps)
        out, err = capsys.readouterr()
        if (n_steps in [0, 5]) or force:
            assert out == expected
        else:
            assert out == ""

class TestEnsembleSatisfiedContinueConditions(object):
    def setup(self):
        cv = paths.CoordinateFunctionCV('x', lambda x: x.xyz[0][0])
        vol_A = paths.CVDefinedVolume(cv, float("-inf"), 0.0)
        vol_B = paths.CVDefinedVolume(cv, 1.0, float("inf"))
        ensembles = [
            paths.LengthEnsemble(1).named("len1"),
            paths.LengthEnsemble(3).named("len3"),
            paths.SequentialEnsemble([
                paths.LengthEnsemble(1) & paths.AllInXEnsemble(vol_A),
                paths.AllOutXEnsemble(vol_A | vol_B),
                paths.LengthEnsemble(1) & paths.AllInXEnsemble(vol_A)
            ]).named('return'),
            paths.SequentialEnsemble([
                paths.LengthEnsemble(1) & paths.AllInXEnsemble(vol_A),
                paths.AllOutXEnsemble(vol_A | vol_B),
                paths.LengthEnsemble(1) & paths.AllInXEnsemble(vol_B)
            ]).named('transition'),
        ]
        self.ensembles = {ens.name: ens for ens in ensembles}
        self.traj_vals = [-0.1, 1.1, 0.5, -0.2, 0.1, -0.3, 0.4, 1.4, -1.0]
        self.trajectory = make_1d_traj(self.traj_vals)
        self.engine = CalvinistDynamics(self.traj_vals)
        self.satisfied_when_traj_len = {
            "len1": 1,
            "len3": 3,
            "return": 6,
            "transition": 8,
        }
        self.conditions = EnsembleSatisfiedContinueConditions(ensembles)


    @pytest.mark.parametrize('trusted', [True, False])
    @pytest.mark.parametrize('traj_len,expected', [
        # expected = (num_calls, num_satisfied)
        (0, (1, 0)),
        (1, (2, 1)),
        (2, (3, 1)),
        (3, (3, 2)),
        (5, (2, 2)),
        (6, (3, 3)),
        (7, (1, 3)),
        (8, (3, 4)),
    ])
    def test_call(self, traj_len, expected, trusted):
        if trusted:
            already_satisfied = [
                self.ensembles[key]
                for key, val in self.satisfied_when_traj_len.items()
                if traj_len > val
            ]
            for ens in already_satisfied:
                self.conditions.satisfied[ens] = True

        traj = self.trajectory[:traj_len]
        mock = Mock(wraps=self.conditions._check_previous_frame)
        self.conditions._check_previous_frame = mock
        expected_calls, expected_satisfied = expected
        result = self.conditions(traj, trusted)
        assert result == (expected_satisfied != 4)
        assert sum(self.conditions.satisfied.values()) == expected_satisfied
        if trusted:
            # only test call count if we're trusted
            assert mock.call_count == expected_calls

    def test_long_traj_untrusted(self):
        traj = make_1d_traj(self.traj_vals + [1.0, 1.2, 1.3, 1.4])
        assert self.conditions(traj) is False

    def test_generate(self):
        init_snap = self.trajectory[0]
        traj = self.engine.generate(init_snap, self.conditions)
        assert len(traj) == 8


@pytest.fixture()
def md_fixture(tps_fixture):
    _, _, engine, sample_set = tps_fixture
    snapshot = sample_set[0].trajectory[0]
    ensemble = paths.LengthEnsemble(5).named('len5')
    return engine, ensemble, snapshot

def print_test(output_storage, engine, ensembles, nsteps, initial_frame):
    print(isinstance(output_storage, paths.Storage))
    print(engine.__uuid__)
    print([e.__uuid__ for e in ensembles])  # only 1?
    print(nsteps)
    print(initial_frame.__uuid__)

@patch('paths_cli.commands.md.md_main', print_test)
def test_md(md_fixture):
    engine, ensemble, snapshot = md_fixture
    runner = CliRunner()
    with runner.isolated_filesystem():
        storage = paths.Storage("setup.nc", 'w')
        storage.save([ensemble, snapshot, engine])
        storage.tags['initial_snapshot'] = snapshot
        storage.close()

        results = runner.invoke(
            md,
            ["setup.nc", '-o', 'foo.nc', '--ensemble', 'len5', '-f',
             'initial_snapshot']
        )
        expected_output = "\n".join([ "True", str(engine.__uuid__),
                                     '[' + str(ensemble.__uuid__) + ']',
                                     'None', str(snapshot.__uuid__)]) + "\n"

        assert results.output == expected_output
        assert results.exit_code == 0

@pytest.mark.parametrize('inp', ['nsteps', 'ensemble'])
def test_md_main(md_fixture, inp):
    tempdir = tempfile.mkdtemp()
    try:
        store_name = os.path.join(tempdir, "md.nc")
        storage = paths.Storage(store_name, mode='w')
        engine, ens, snapshot = md_fixture
        if inp == 'nsteps':
            nsteps, ensembles = 5, None
        elif inp == 'ensemble':
            nsteps, ensembles = None, [ens]
        else:
            raise RuntimeError("pytest went crazy")

        traj, foo = md_main(
            output_storage=storage,
            engine=engine,
            ensembles=ensembles,
            nsteps=nsteps,
            initial_frame=snapshot
        )
        assert isinstance(traj, paths.Trajectory)
        assert foo is None
        assert len(traj) == 5
        assert len(storage.trajectories) == 1
        storage.close()
    finally:
        os.remove(store_name)
        os.rmdir(tempdir)

def test_md_main_error(md_fixture):
    engine, ensemble, snapshot = md_fixture
    with pytest.raises(RuntimeError):
        md_main(output_storage=None,
                engine=engine,
                ensembles=[ensemble],
                nsteps=5,
                initial_frame=snapshot)

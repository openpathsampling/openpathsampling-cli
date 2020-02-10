import os

import pytest
from click.testing import CliRunner

from paths_cli.commands.append import *

import openpathsampling as paths

def make_input_file(tps_network_and_traj):
    input_file = paths.Storage("setup.py", mode='w')
    for obj in tps_network_and_traj:
        input_file.save(obj)

    input_file.tags['template'] = input_file.snapshots[0]
    input_file.close()
    return "setup.py"

def test_append(tps_network_and_traj):
    runner = CliRunner()
    with runner.isolated_filesystem():
        in_file = make_input_file(tps_network_and_traj)
        result = runner.invoke(append, [in_file, '-a', 'output.nc',
                                        '--volume', 'A', '--volume', 'B'])
        assert result.exit_code == 0
        assert result.exception is None
        storage = paths.Storage('output.nc', mode='r')
        assert len(storage.volumes) == 2
        assert len(storage.snapshots) == 0
        storage.volumes['A']  # smoke tests that we can load
        storage.volumes['B']
        storage.close()

        result = runner.invoke(append, [in_file, '-a', 'output.nc',
                                        '--tag', 'template'])
        storage = paths.Storage('output.nc', mode='r')
        assert len(storage.volumes) == 2
        assert len(storage.snapshots) == 2  # one snapshot + reverse

@pytest.mark.parametrize('n_objects', [0, 2])
def test_append_tag_error(tps_network_and_traj, n_objects):
    objs = {2: ['--volume', "A", '--volume', "B"], 0: []}[n_objects]
    runner = CliRunner()
    with runner.isolated_filesystem():
        in_file = make_input_file(tps_network_and_traj)
        result = runner.invoke(append,
                               [in_file, '-a', "output.nc"] + objs
                               + ["--save-tag", "foo"])
        assert isinstance(result.exception, RuntimeError)
        assert "Can't identify the object to tag" in str(result.exception)

def test_append_tag(tps_network_and_traj):
    runner = CliRunner()
    with runner.isolated_filesystem():
        in_file = make_input_file(tps_network_and_traj)
        result = runner.invoke(append,
                               [in_file, '-a', "output.nc",
                                '--tag', 'template', '--save-tag', 'foo'])
        assert result.exit_code == 0
        assert result.exception is None

        storage = paths.Storage("output.nc", mode='r')
        assert len(storage.snapshots) == 2
        assert len(storage.tags) == 1
        assert storage.tags['foo'] is not None
        storage.close()

def test_append_same_tag(tps_network_and_traj):
    runner = CliRunner()
    with runner.isolated_filesystem():
        in_file = make_input_file(tps_network_and_traj)
        result = runner.invoke(append,
                               [in_file, '-a', "output.nc",
                                '--tag', 'template'])
        assert result.exit_code == 0
        assert result.exception is None

        storage = paths.Storage("output.nc", mode='r')
        assert len(storage.snapshots) == 2
        assert len(storage.tags) == 1
        assert storage.tags['template'] is not None
        storage.close()

def test_append_remove_tag(tps_network_and_traj):
    runner = CliRunner()
    with runner.isolated_filesystem():
        in_file = make_input_file(tps_network_and_traj)
        result = runner.invoke(append,
                               [in_file, '-a', "output.nc",
                                "--tag", 'template', '--save-tag', ''])
        print(result.output)
        assert result.exception is None
        assert result.exit_code == 0

        storage = paths.Storage("output.nc", mode='r')
        assert len(storage.snapshots) == 2
        assert len(storage.tags) == 0
        storage.close()


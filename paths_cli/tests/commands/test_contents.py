import os
import tempfile
import pytest
from unittest.mock import patch
from click.testing import CliRunner

import openpathsampling as paths

from paths_cli.commands.contents import *

def test_contents(tps_fixture):
    # we just do a full integration test of this one
    scheme, network, engine, init_conds = tps_fixture
    runner = CliRunner()
    with runner.isolated_filesystem():
        storage = paths.Storage("setup.nc", 'w')
        for obj in tps_fixture:
            storage.save(obj)
        storage.tags['initial_conditions'] = init_conds

        results = runner.invoke(contents, ['setup.nc'])
        cwd = os.getcwd()
        expected = [
            f"Storage @ '{cwd}/setup.nc'",
            "CVs: 1 item", "* x",
            "Volumes: 8 items", "* A", "* B", "* plus 6 unnamed items",
            "Engines: 2 items", "* flat", "* plus 1 unnamed item",
            "Networks: 1 item", "* 1 unnamed item",
            "Move Schemes: 1 item", "* 1 unnamed item",
            "Simulations: 0 items",
            "Tags: 1 item", "* initial_conditions",
            "", "Data Objects:",
            "Steps: 0 unnamed items",
            "Move Changes: 0 unnamed items",
            "SampleSets: 1 unnamed item",
            "Trajectories: 1 unnamed item",
            f"Snapshots: {2*len(init_conds[0])} unnamed items", ""
        ]
        assert results.exit_code == 0
        assert results.output.split('\n') == expected
        for truth, beauty in zip(expected, results.output.split('\n')):
            assert truth == beauty

@pytest.mark.parametrize('table', ['volumes', 'trajectories', 'tags'])
def test_contents_table(tps_fixture, table):
    scheme, network, engine, init_conds = tps_fixture
    runner = CliRunner()
    with runner.isolated_filesystem():
        storage = paths.Storage("setup.nc", 'w')
        for obj in tps_fixture:
            storage.save(obj)
        storage.tags['initial_conditions'] = init_conds

        results = runner.invoke(contents, ['setup.nc', '--table', table])
        cwd = os.getcwd()
        expected = {
            'volumes': [
                f"Storage @ '{cwd}/setup.nc'",
                "volumes: 8 items", "* A", "* B", "* plus 6 unnamed items",
                ""
            ],
            'trajectories': [
                f"Storage @ '{cwd}/setup.nc'",
                "trajectories: 1 unnamed item",
                ""
            ],
            'tags': [
                f"Storage @ '{cwd}/setup.nc'",
                "tags: 1 item",
                "* initial_conditions",
                ""
            ],
        }[table]
        assert results.output.split("\n") == expected
        assert results.exit_code == 0

def test_contents_table_error():
    runner = CliRunner()
    with runner.isolated_filesystem():
        storage = paths.Storage("temp.nc", mode='w')
        storage.close()
        results = runner.invoke(contents, ['temp.nc', '--table', 'foo'])
        assert results.exit_code != 0

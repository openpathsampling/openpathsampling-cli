import os
import pytest
from unittest.mock import patch
import tempfile
from click.testing import CliRunner

import openpathsampling as paths

from paths_cli.commands.pathsampling import *

def print_test(output_storage, scheme, init_conds, n_steps):
    print(isinstance(output_storage, paths.Storage))
    print(scheme.__uuid__)
    print(init_conds.__uuid__)
    print(n_steps)

@patch('paths_cli.commands.pathsampling.pathsampling_main', print_test)
def test_pathsampling(tps_fixture):
    scheme, _, _, init_conds = tps_fixture
    runner = CliRunner()
    with runner.isolated_filesystem():
        storage = paths.Storage("setup.nc", 'w')
        for obj in tps_fixture:
            storage.save(obj)
        storage.tags['initial_conditions'] = init_conds

        results = runner.invoke(pathsampling, ['setup.nc', '-o', 'foo.nc',
                                               '-n', '1000'])
        expected_output = (f"True\n{scheme.__uuid__}\n{init_conds.__uuid__}"
                           "\n1000\n")

        assert results.output == expected_output
        assert results.exit_code == 0


def test_pathsampling_main(tps_fixture):
    scheme, _, _, init_conds = tps_fixture
    with CliRunner().isolated_filesystem():
        storage = paths.Storage("tps.nc", mode='w')
        final, sim = pathsampling_main(storage, scheme, init_conds, 10)
        assert isinstance(final, paths.SampleSet)
        assert isinstance(sim, paths.PathSampling)
        assert len(storage.steps) == 11
        assert len(storage.schemes) == 1



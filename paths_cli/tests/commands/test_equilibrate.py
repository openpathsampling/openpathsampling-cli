import os
import pytest
from unittest.mock import patch
import tempfile
from click.testing import CliRunner

from paths_cli.commands.equilibrate import *

import openpathsampling as paths

def print_test(output_storage, scheme, init_conds, multiplier, extra_steps):
    print(isinstance(output_storage, paths.Storage))
    print(scheme.__uuid__)
    print(init_conds.__uuid__)
    print(multiplier, extra_steps)


@patch('paths_cli.commands.equilibrate.equilibrate_main', print_test)
def test_equilibrate(tps_fixture):
    # integration test (click and parameters)
    scheme, network, engine, init_conds = tps_fixture
    runner = CliRunner()
    with runner.isolated_filesystem():
        storage = paths.Storage("setup.nc", 'w')
        for obj in tps_fixture:
            storage.save(obj)
        storage.tags['initial_conditions'] = init_conds

        results = runner.invoke(
            equilibrate,
            ["setup.nc", "-o", "foo.nc"]
        )
        out_str = "True\n{schemeid}\n{condsid}\n1 0\n"
        expected_output = out_str.format(schemeid=scheme.__uuid__,
                                         condsid=init_conds.__uuid__)
        assert results.exit_code == 0
        assert results.output == expected_output

def test_equilibrate_main(tps_fixture):
    # smoke test
    tempdir = tempfile.mkdtemp()
    store_name = os.path.join(tempdir, "equil.nc")
    try:
        storage = paths.Storage(store_name, mode='w')
        scheme, network, engine, init_conds = tps_fixture
        equilibrated, sim = equilibrate_main(storage, scheme, init_conds,
                                             multiplier=1, extra_steps=1)
        assert isinstance(equilibrated, paths.SampleSet)
        assert isinstance(sim, paths.PathSampling)
    finally:
        if os.path.exists(store_name):
            os.remove(store_name)
        os.rmdir(tempdir)

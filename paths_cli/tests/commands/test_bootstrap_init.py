import pytest
from click.testing import CliRunner
from unittest.mock import patch

from paths_cli.commands.bootstrap_init import *
import openpathsampling as paths

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


def test_bootstrap_init_main(tis_fixture, tmp_path):
    scheme, network, engine, init_conds = tis_fixture
    init_frame = init_conds[0][0]
    assert len(network.transitions) == 1
    transition = list(network.transitions.values())[0]
    output_storage = paths.Storage(tmp_path / "output.nc", mode='w')
    init_conds, bootstrapper = bootstrap_init_main(init_frame, network,
                                                   engine, transition,
                                                   output_storage)

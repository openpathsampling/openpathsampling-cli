import pytest
from unittest import mock
from paths_cli.tests.compiling.utils import mock_compiler
import numpy as np

import yaml
import openpathsampling as paths

from paths_cli.compiling.networks import *

_COMPILERS_LOC = 'paths_cli.compiling.root_compiler._COMPILERS'

@pytest.fixture
def unidirectional_tis_compiler(cv_and_states):
    paths.InterfaceSet._reset()
    cv, state_A, state_B = cv_and_states
    return {
        'cv': mock_compiler('cv', named_objs={'cv': cv}),
        'volume': mock_compiler('volume', named_objs={
            "A": state_A, "B": state_B
        }),
        'interface_set': mock_compiler(
            'interface_set',
            type_dispatch={
                'volume-interface-set': VOLUME_INTERFACE_SET_PLUGIN
            }
        ),
    }


def test_build_tps_network(cv_and_states):
    _, state_A, state_B = cv_and_states
    yml = "\n".join(["initial_states:", "  - A", "final_states:", "  - B"])
    dct = yaml.load(yml, yaml.FullLoader)
    compiler = {
        'volume': mock_compiler('volume', named_objs={"A": state_A,
                                                      "B": state_B}),
    }
    with mock.patch.dict(_COMPILERS_LOC, compiler):
        network = TPS_NETWORK_PLUGIN(dct)
    assert isinstance(network, paths.TPSNetwork)
    assert len(network.initial_states) == len(network.final_states) == 1
    assert network.initial_states[0] == state_A
    assert network.final_states[0] == state_B


def test_build_mistis_network(cv_and_states, unidirectional_tis_compiler):
    cv, state_A, state_B = cv_and_states
    mistis_dict = {
        'interface_sets': [
            {
                'initial_state': "A",
                'final_state': "B",
                'cv': 'cv',
                'minvals': 'float("-inf")',
                'maxvals': "np.array([0, 0.1, 0.2]) * np.pi"
            },
            {
                'initial_state': "B",
                'final_state': "A",
                'cv': 'cv',
                'minvals': "np.array([1.0, 0.9, 0.8])",
                'maxvals': "float('inf')",
            }
        ]
    }

    with mock.patch.dict(_COMPILERS_LOC, unidirectional_tis_compiler):
        network = MISTIS_NETWORK_PLUGIN(mistis_dict)

    assert isinstance(network, paths.MISTISNetwork)
    assert len(network.sampling_transitions) == 2
    assert len(network.transitions) == 2
    assert list(network.transitions) == [(state_A, state_B),
                                         (state_B, state_A)]

def test_build_tis_network(cv_and_states, unidirectional_tis_compiler):
    cv, state_A, state_B = cv_and_states
    tis_dict = {
        'initial_state': "A",
        'final_state': "B",
        'cv': "cv",
        'minvals': 'float("inf")',
        'maxvals': "np.array([0, 0.1, 0.2]) * np.pi",
    }

    with mock.patch.dict(_COMPILERS_LOC, unidirectional_tis_compiler):
        network = TIS_NETWORK_PLUGIN(tis_dict)

    assert isinstance(network, paths.MISTISNetwork)
    assert len(network.sampling_transitions) == 1
    assert len(network.transitions) == 1
    assert list(network.transitions) == [(state_A, state_B)]

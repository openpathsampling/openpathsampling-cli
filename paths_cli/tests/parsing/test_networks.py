import pytest
from unittest import mock
import numpy as np

import yaml
import openpathsampling as paths

from paths_cli.parsing.networks import *


def check_unidirectional_tis(results, state_A, state_B, cv):
    assert len(results) == 1
    trans_info = results['trans_info']
    assert len(trans_info) == 1
    assert len(trans_info[0]) == 3
    trans = trans_info[0]
    assert isinstance(trans, tuple)
    assert trans[0] == state_A
    assert trans[2] == state_B
    assert isinstance(trans[1], paths.VolumeInterfaceSet)
    ifaces = trans[1]
    assert ifaces.cv == cv
    assert ifaces.minvals == float("-inf")
    np.testing.assert_allclose(ifaces.maxvals,
                               [0, np.pi / 10.0, np.pi / 5.0])


def test_mistis_trans_info(cv_and_states):
    cv, state_A, state_B = cv_and_states
    dct = {
        'transitions': [{
            'initial_state': "A",
            'final_state': "B",
            'interfaces': {
                'cv': 'cv',
                'minvals': 'float("-inf")',
                'maxvals': "np.array([0, 0.1, 0.2]) * np.pi"
            }
        }]
    }
    patch_base = 'paths_cli.parsing.networks'

    with mock.patch.dict(f"{patch_base}.volume_parser.named_objs",
                          {"A": state_A, "B": state_B}), \
          mock.patch.dict(f"{patch_base}.cv_parser.named_objs",
                          {'cv': cv}):
        results = mistis_trans_info(dct)

    check_unidirectional_tis(results, state_A, state_B, cv)
    paths.InterfaceSet._reset()


def test_tis_trans_info(cv_and_states):
    cv, state_A, state_B = cv_and_states
    dct = {
        'initial_state': "A",
        'final_state': "B",
        'interfaces': {
            'cv': 'cv',
            'minvals': 'float("-inf")',
            'maxvals': 'np.array([0, 0.1, 0.2]) * np.pi',
        }
    }

    patch_base = 'paths_cli.parsing.networks'
    with mock.patch.dict(f"{patch_base}.volume_parser.named_objs",
                          {"A": state_A, "B": state_B}), \
          mock.patch.dict(f"{patch_base}.cv_parser.named_objs",
                          {'cv': cv}):
        results = tis_trans_info(dct)

    check_unidirectional_tis(results, state_A, state_B, cv)
    paths.InterfaceSet._reset()


def test_build_tps_network(cv_and_states):
    _, state_A, state_B = cv_and_states
    yml = "\n".join(["initial_states:", "  - A", "final_states:", "  - B"])
    dct = yaml.load(yml, yaml.FullLoader)
    patch_loc = 'paths_cli.parsing.networks.volume_parser.named_objs'
    with mock.patch.dict(patch_loc, {"A": state_A, "B": state_B}):
        network = build_tps_network(dct)
    assert isinstance(network, paths.TPSNetwork)
    assert len(network.initial_states) == len(network.final_states) == 1
    assert network.initial_states[0] == state_A
    assert network.final_states[0] == state_B

def test_build_mistis_network():
    pytest.skip()

def test_build_tis_network():
    pytest.skip()

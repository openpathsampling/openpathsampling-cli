import pytest

from paths_cli.compiling.shooting import *
from paths_cli.compiling.shooting import _remapping_gaussian_stddev
import openpathsampling as paths
from paths_cli.tests.compiling.utils import mock_compiler

from unittest.mock import patch
from openpathsampling.tests.test_helpers import make_1d_traj

_COMPILERS_LOC = 'paths_cli.compiling.root_compiler._COMPILERS'

def test_remapping_gaussian_stddev(cv_and_states):
    cv, _, _ = cv_and_states
    dct = {'cv': cv, 'mean': 1.0, 'stddev': 2.0}
    expected = {'collectivevariable': cv, 'l_0': 1.0, 'alpha': 0.125}
    results = _remapping_gaussian_stddev(dct)
    assert results == expected

def test_build_gaussian_selector(cv_and_states):
    cv, _, _ = cv_and_states
    dct = {'cv': 'x', 'mean': 1.0, 'stddev': 2.0}
    compiler = {'cv': mock_compiler('cv', named_objs={'x': cv})}
    with patch.dict(_COMPILERS_LOC, compiler):
        sel = build_gaussian_selector(dct)

    assert isinstance(sel, paths.GaussianBiasSelector)
    traj = make_1d_traj([1.0, 1.0, 1.0])
    assert sel.f(traj[1], traj) == 1.0

def test_build_uniform_selector():
    sel = build_uniform_selector({})
    assert isinstance(sel, paths.UniformSelector)
    traj = make_1d_traj([1.0, 1.0, 1.0])
    assert sel.f(traj[1], traj) == 1.0

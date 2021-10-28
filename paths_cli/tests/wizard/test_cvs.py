import pytest
from unittest import mock
import numpy as np

from functools import partial

from paths_cli.tests.wizard.mock_wizard import mock_wizard

from paths_cli.wizard.cvs import (
    TOPOLOGY_CV_PREREQ, _get_atom_indices, MDTRAJ_DISTANCE, MDTRAJ_ANGLE,
    MDTRAJ_DIHEDRAL, COORDINATE_CV
)

import openpathsampling as paths
from openpathsampling.experimental.storage.collective_variables import \
        MDTrajFunctionCV
from openpathsampling.tests.test_helpers import make_1d_traj

@pytest.mark.parametrize('n_engines', [0, 1, 2])
def test_TOPOLOGY_CV_PREREQ(ad_engine, n_engines):
    inputs = {0: [], 1: [], 2: ['1']}[n_engines]
    wizard = mock_wizard(inputs)
    engines = [ad_engine, paths.engines.NoEngine(None).named('foo')]
    wizard.engines = {eng.name: eng for eng in engines[:n_engines]}
    def mock_register(obj, obj_type, store_name):
        wizard.engines[obj.name] = obj
    wizard.register = mock_register

    mock_engines = mock.Mock(return_value=ad_engine)
    patch_loc = 'paths_cli.wizard.cvs.TOPOLOGY_CV_PREREQ.create_func'
    with mock.patch(patch_loc, new=mock_engines):
        topology_result = TOPOLOGY_CV_PREREQ(wizard)
    topology = topology_result['topology'][0]
    assert isinstance(topology, paths.engines.MDTrajTopology)

@pytest.mark.parametrize('inputs', [
    (['[[1, 2]]']), (['1, 2']),
    (['[[1, 2, 3]]', '[[1, 2]]']),
])
def test_get_atom_indices(ad_engine, inputs):
    wizard = mock_wizard(inputs)
    arr = _get_atom_indices(wizard, ad_engine.topology, 2, "use")
    np.testing.assert_array_equal(arr, np.array([[1, 2]]))
    assert wizard.console.input_call_count == len(inputs)
    if len(inputs) > 1:
        assert "I didn't understand" in wizard.console.log_text

def _mdtraj_function_test(wizard, func, md_func, ad_openmm, ad_engine):
    md = pytest.importorskip('mdtraj')
    wizard.engines[ad_engine.name] = ad_engine
    with ad_openmm.as_cwd():
        cv = func(wizard)
        pdb = md.load('ad.pdb')
    assert isinstance(cv, MDTrajFunctionCV)
    traj = paths.engines.openmm.trajectory_from_mdtraj(pdb)
    np.testing.assert_array_almost_equal(md_func(pdb)[0], cv(traj))

def test_distance(ad_openmm, ad_engine):
    md = pytest.importorskip('mdtraj')
    wizard = mock_wizard(['0, 1'])
    md_func = partial(md.compute_distances, atom_pairs=[[0, 1]])
    _mdtraj_function_test(wizard, MDTRAJ_DISTANCE, md_func, ad_openmm,
                          ad_engine)

def test_angle(ad_openmm, ad_engine):
    md = pytest.importorskip('mdtraj')
    wizard = mock_wizard(['0, 1, 2'])
    md_func = partial(md.compute_angles, angle_indices=[[0, 1, 2]])
    _mdtraj_function_test(wizard, MDTRAJ_ANGLE, md_func, ad_openmm, ad_engine)

def test_dihedral(ad_openmm, ad_engine):
    md = pytest.importorskip('mdtraj')
    wizard = mock_wizard(['0, 1, 2, 3'])
    md_func = partial(md.compute_dihedrals, indices=[[0, 1, 2, 3]])
    _mdtraj_function_test(wizard, MDTRAJ_DIHEDRAL, md_func, ad_openmm,
                          ad_engine)

@pytest.mark.parametrize('inputs', [
    (['0', 'x']), ('foo', '0', 'x'), (['0', 'q', 'x'])
])
def test_coordinate(inputs):
    wizard = mock_wizard(inputs)
    cv = COORDINATE_CV(wizard)
    traj = make_1d_traj([5.0])
    assert cv(traj[0]) == 5.0
    if 'foo' in inputs:
        assert "I can't make an atom index" in wizard.console.log_text
    if 'q' in inputs:
        assert "Please select one of" in wizard.console.log_text

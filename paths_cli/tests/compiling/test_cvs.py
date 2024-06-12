import pytest
import yaml

from openpathsampling.tests.test_helpers import data_filename
import numpy.testing as npt

from paths_cli.compiling.cvs import *
from paths_cli.compiling.errors import InputError
import openpathsampling as paths
from openpathsampling.experimental.storage.collective_variables \
        import MDTrajFunctionCV
import mdtraj as md

from paths_cli.compat.openmm import HAS_OPENMM


class TestMDTrajFunctionCV:
    def setup_method(self):
        self.ad_pdb = data_filename("ala_small_traj.pdb")
        self.yml = "\n".join([
            "name: phi", "type: mdtraj", "topology: " + self.ad_pdb,
            "period_min: -np.pi", "period_max: np.pi",
            "func: {func}",
            "kwargs:", "  {kwargs}",
        ])
        self.kwargs = "indices: [[4, 6, 8, 14]]"

    def test_build_mdtraj_function_cv(self):
        if not HAS_OPENMM:
            pytest.skip("Requires OpenMM for ops_load_trajectory")
        yml = self.yml.format(kwargs=self.kwargs, func="compute_dihedrals")
        dct = yaml.load(yml, Loader=yaml.FullLoader)
        cv = MDTRAJ_CV_PLUGIN(dct)
        assert isinstance(cv, MDTrajFunctionCV)
        assert cv.func == md.compute_dihedrals
        md_trj = md.load(self.ad_pdb)
        ops_trj = paths.engines.openmm.tools.ops_load_trajectory(self.ad_pdb)
        expected = md.compute_dihedrals(md_trj, indices=[[4,6,8,14]])
        npt.assert_array_almost_equal(cv(ops_trj).reshape(expected.shape),
                                      expected)

    def test_bad_mdtraj_function_name(self):
        yml = self.yml.format(kwargs=self.kwargs, func="foo")
        dct = yaml.load(yml, Loader=yaml.FullLoader)
        with pytest.raises(InputError, match="foo"):
            cv = MDTRAJ_CV_PLUGIN(dct)

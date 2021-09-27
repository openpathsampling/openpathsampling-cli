import pytest
from openpathsampling.tests.test_helpers import data_filename
from unittest.mock import patch, Mock

from paths_cli.compiling.topology import *
from paths_cli.compiling.errors import InputError
import paths_cli.compiling.root_compiler
from paths_cli.tests.compiling.utils import mock_compiler


class TestBuildTopology:
    def test_build_topology_file(self):
        ad_pdb = data_filename("ala_small_traj.pdb")
        topology = build_topology(ad_pdb)
        assert topology.n_spatial == 3
        assert topology.n_atoms == 1651

    def test_build_topology_engine(self, flat_engine):
        patch_loc = 'paths_cli.compiling.root_compiler._COMPILERS'
        compiler = mock_compiler('engine', named_objs={'flat': flat_engine})
        compilers = {'engine': compiler}
        with patch.dict(patch_loc, compilers):
            topology = build_topology('flat')
            assert topology.n_spatial == 3
            assert topology.n_atoms == 1

    def test_build_topology_fail(self):
        patch_loc = 'paths_cli.compiling.root_compiler._COMPILERS'
        compilers = {'engine': mock_compiler('engine')}
        with patch.dict(patch_loc, compilers):
            with pytest.raises(InputError, match="foo"):
                topology = build_topology('foo')

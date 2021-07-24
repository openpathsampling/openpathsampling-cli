import pytest
from openpathsampling.tests.test_helpers import data_filename
from unittest.mock import patch

from paths_cli.parsing.topology import *
from paths_cli.parsing.errors import InputError

class TestBuildTopology:
    def test_build_topology_file(self):
        ad_pdb = data_filename("ala_small_traj.pdb")
        topology = build_topology(ad_pdb)
        assert topology.n_spatial == 3
        assert topology.n_atoms == 1651

    def test_build_topology_engine(self, flat_engine):
        patch_loc = 'paths_cli.parsing.engines.engine_parser.named_objs'
        with patch.dict(patch_loc, {'flat': flat_engine}):
            topology = build_topology('flat')
            assert topology.n_spatial == 3
            assert topology.n_atoms == 1

    def test_build_topology_fail(self):
        with pytest.raises(InputError):
            topology = build_topology('foo')

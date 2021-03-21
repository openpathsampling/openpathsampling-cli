import pytest
from openpathsampling.tests.test_helpers import data_filename

from paths_cli.parsing.topology import *

class TestBuildTopology:
    def test_build_topology_file(self):
        ad_pdb = data_filename("ala_small_traj.pdb")
        topology = build_topology(ad_pdb)
        assert topology.n_spatial == 3
        assert topology.n_atoms == 1651

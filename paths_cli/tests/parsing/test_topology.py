import pytest
from openpathsampling.tests.test_helpers import data_filename
from unittest.mock import patch, Mock

from paths_cli.parsing.topology import *
from paths_cli.parsing.errors import InputError
import paths_cli.parsing.root_parser
from paths_cli.tests.parsing.utils import mock_parser


class TestBuildTopology:
    def test_build_topology_file(self):
        ad_pdb = data_filename("ala_small_traj.pdb")
        topology = build_topology(ad_pdb)
        assert topology.n_spatial == 3
        assert topology.n_atoms == 1651

    def test_build_topology_engine(self, flat_engine):
        patch_loc = 'paths_cli.parsing.root_parser._PARSERS'
        parser = mock_parser('engine', named_objs={'flat': flat_engine})
        parsers = {'engine': parser}
        with patch.dict(patch_loc, parsers):
            topology = build_topology('flat')
            assert topology.n_spatial == 3
            assert topology.n_atoms == 1

    def test_build_topology_fail(self):
        patch_loc = 'paths_cli.parsing.root_parser._PARSERS'
        parsers = {'engine': mock_parser('engine')}
        with patch.dict(patch_loc, parsers):
            with pytest.raises(InputError):
                topology = build_topology('foo')

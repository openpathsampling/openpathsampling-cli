import pytest
import yaml
import os

from paths_cli.parsing.engines import *
from paths_cli.parsing.errors import InputError
import openpathsampling as paths

from openpathsampling.engines import openmm as ops_openmm
import mdtraj as md


class TestOpenMMEngineBuilder(object):
    def setup(self):
        self.cwd = os.getcwd()
        self.yml = "\n".join([
            "type: openmm", "name: engine", "system: system.xml",
            "integrator: integrator.xml", "topology: ad.pdb",
            "n_steps_per_frame: 10", "n_frames_max: 10000"
        ])
        pass

    def teardown(self):
        os.chdir(self.cwd)

    def _create_files(self, tmpdir):
        mm = pytest.importorskip('simtk.openmm')
        openmmtools = pytest.importorskip('openmmtools')
        unit = pytest.importorskip('simtk.unit')
        ad = openmmtools.testsystems.AlanineDipeptideVacuum()
        integrator = openmmtools.integrators.VVVRIntegrator(
            300*unit.kelvin, 1.0/unit.picosecond, 2.0*unit.femtosecond
        )
        with open(os.path.join(tmpdir, 'system.xml'), mode='w') as f:
            f.write(mm.XmlSerializer.serialize(ad.system))
        with open(os.path.join(tmpdir, 'integrator.xml'), mode='w') as f:
            f.write(mm.XmlSerializer.serialize(integrator))

        trj = md.Trajectory(ad.positions.value_in_unit(unit.nanometer),
                            topology=ad.mdtraj_topology)
        trj.save(os.path.join(tmpdir, "ad.pdb"))

    def test_load_openmm_xml(self, tmpdir):
        mm = pytest.importorskip('simtk.openmm')
        self._create_files(tmpdir)
        os.chdir(tmpdir)
        for fname in ['system.xml', 'integrator.xml', 'ad.pdb']:
            assert fname in os.listdir()

        integ = load_openmm_xml('integrator.xml', {})
        assert isinstance(integ, mm.CustomIntegrator)
        sys = load_openmm_xml('system.xml', {})
        assert isinstance(sys, mm.System)

    def test_openmm_options(self):
        dct = yaml.load(self.yml, yaml.FullLoader)
        dct = openmm_options(dct)
        assert dct == {'type': 'openmm', 'name': 'engine',
                       'system': 'system.xml',
                       'integrator': 'integrator.xml',
                       'topology': 'ad.pdb',
                       'options': {'n_steps_per_frame': 10,
                                   'n_frames_max': 10000}}

    def test_build_openmm_engine(self, tmpdir):
        self._create_files(tmpdir)
        os.chdir(tmpdir)
        dct = yaml.load(self.yml, yaml.FullLoader)
        engine = build_openmm_engine(dct, {})
        assert isinstance(engine, ops_openmm.Engine)
        snap = ops_openmm.tools.ops_load_trajectory('ad.pdb')[0]
        engine.current_snapshot = snap
        engine.simulation.minimizeEnergy()
        engine.generate_next_frame()

import pytest

import openpathsampling as paths
import mdtraj as md

@pytest.fixture
def ad_openmm(tmpdir):
    """
    Provide directory with files to start alanine depeptide sim in OpenMM
    """
    mm = pytest.importorskip('simtk.openmm')
    u = pytest.importorskip('simtk.unit')
    openmmtools = pytest.importorskip('openmmtools')
    md = pytest.importorskip('mdtraj')
    testsystem = openmmtools.testsystems.AlanineDipeptideVacuum()
    integrator = openmmtools.integrators.VVVRIntegrator(
        300 * u.kelvin,
        1.0 / u.picosecond,
        2.0 * u.femtosecond
    )
    traj = md.Trajectory([testsystem.positions.value_in_unit(u.nanometer)],
                         topology=testsystem.mdtraj_topology)
    files = {'integrator.xml': integrator,
             'system.xml': testsystem.system}
    with tmpdir.as_cwd():
        for fname, obj in files.items():
            with open(fname, mode='w') as f:
                f.write(mm.XmlSerializer.serialize(obj))

        traj.save('ad.pdb')

    return tmpdir

@pytest.fixture
def ad_engine(ad_openmm):
    with ad_openmm.as_cwd():
        pdb = md.load('ad.pdb')
        topology = paths.engines.openmm.topology.MDTrajTopology(
            pdb.topology
        )
        engine = paths.engines.openmm.Engine(
            system='system.xml',
            integrator='integrator.xml',
            topology=topology,
            options={'n_steps_per_frame': 10,
                     'n_frames_max': 10000}
        ).named('ad_engine')
    return engine

# TODO: add fixtures for all the AD things: CVs, states

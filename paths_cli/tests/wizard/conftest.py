import pytest

import openpathsampling as paths
import mdtraj as md

from paths_cli.compat.openmm import HAS_OPENMM, mm, unit

from paths_cli.wizard import pause


@pytest.fixture(autouse=True, scope='session')
def pause_style_testing():
    pause.set_pause_style('testing')
    yield


# TODO: this isn't wizard-specific, and should be moved somwhere more
# generally useful (like, oh, maybe openpathsampling.tests.fixtures?)
@pytest.fixture
def ad_openmm(tmpdir):
    """
    Provide directory with files to start alanine depeptide sim in OpenMM
    """
    # switch back to importorskip when we drop OpenMM < 7.6
    if not HAS_OPENMM:
        pytest.skip("could not import openmm")
    # mm = pytest.importorskip('simtk.openmm')
    # u = pytest.importorskip('simtk.unit')
    openmmtools = pytest.importorskip('openmmtools')
    md = pytest.importorskip('mdtraj')
    testsystem = openmmtools.testsystems.AlanineDipeptideVacuum()
    integrator = openmmtools.integrators.VVVRIntegrator(
        300 * unit.kelvin,
        1.0 / unit.picosecond,
        2.0 * unit.femtosecond
    )
    traj = md.Trajectory(
        [testsystem.positions.value_in_unit(unit.nanometer)],
        topology=testsystem.mdtraj_topology
    )
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
        topology = paths.engines.MDTrajTopology(
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

@pytest.fixture
def toy_engine():
    pes = (paths.engines.toy.OuterWalls([1.0, 1.0], [1.0, 1.0])
           + paths.engines.toy.Gaussian(-1.0, [12.0, 12.0], [-0.5, 0.0])
           + paths.engines.toy.Gaussian(-1.0, [12.0, 12.0], [0.5, 0.0]))
    topology = paths.engines.toy.Topology(n_spatial=2,
                                          masses=[1.0],
                                          pes=pes)
    integ = paths.engines.toy.LangevinBAOABIntegrator(
        dt=0.02,
        temperature=0.1,
        gamma=2.5
    )
    options = {'integ': integ,
               'n_frames_max': 5000,
               'n_steps_per_frame': 1}
    engine = paths.engines.toy.Engine(
        options=options,
        topology=topology
    ).named('toy-engine')
    return engine


@pytest.fixture
def tps_network():
    cv = paths.CoordinateFunctionCV('x', lambda s: s.xyz[0][0])
    state_A = paths.CVDefinedVolume(cv, float("-inf"), 0).named("A")
    state_B = paths.CVDefinedVolume(cv, 0, float("inf")).named("B")
    network = paths.TPSNetwork(state_A, state_B).named('tps-network')
    return network

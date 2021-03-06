from paths_cli.wizard.errors import FILE_LOADING_ERROR_MSG, not_installed
from paths_cli.wizard.core import get_object
try:
    from simtk import openmm as mm
    import mdtraj as md
except ImportError:
    HAS_OPENMM = False
else:
    HAS_OPENMM = True


def _openmm_serialization_helper(wizard, user_input):  # no-cov
    wizard.say("You can write OpenMM objects like systems and integrators "
               "to XML files using the XMLSerializer class. Learn more "
               "here: \n"
               "http://docs.openmm.org/latest/api-python/generated/"
               "simtk.openmm.openmm.XmlSerializer.html")


@get_object
def _load_openmm_xml(wizard, obj_type):
    xml = wizard.ask(
        f"Where is the XML file for your OpenMM {obj_type}?",
        helper=_openmm_serialization_helper
    )
    try:
        with open(xml, 'r') as xml_f:
            data = xml_f.read()
        obj = mm.XmlSerializer.deserialize(data)
    except Exception as e:
        wizard.exception(FILE_LOADING_ERROR_MSG, e)
    else:
        return obj

@get_object
def _load_topology(wizard):
    import openpathsampling as paths
    filename = wizard.ask("Where is a PDB file describing your system?")
    try:
        snap = paths.engines.openmm.snapshot_from_pdb(filename)
    except Exception as e:
        wizard.exception(FILE_LOADING_ERROR_MSG, e)
        return

    return snap.topology

def openmm(wizard):
    import openpathsampling as paths
    # quick exit if not installed; but should be impossible to get here
    if not HAS_OPENMM:
        not_installed("OpenMM", "engine")
        return

    wizard.say("Great! OpenMM gives you a lot of flexibility. "
               "To use OpenMM in OPS, you need to provide XML versions of "
               "your system, integrator, and some file containing "
               "topology information.")
    system = _load_openmm_xml(wizard, 'system')
    integrator = _load_openmm_xml(wizard, 'integrator')
    topology = _load_topology(wizard)

    n_steps_per_frame = wizard.ask_custom_eval(
        "How many MD steps per saved frame?", type_=int
    )
    n_frames_max = wizard.ask_custom_eval(
        "How many frames before aborting a trajectory?", type_=int
    )
    # TODO: assemble the OpenMM simulation
    engine = paths.engines.openmm.Engine(
        topology=topology,
        system=system,
        integrator=integrator,
        options={
            'n_steps_per_frame': n_steps_per_frame,
            'n_frames_max': n_frames_max,
        }
    )
    return engine

SUPPORTED = {"OpenMM": openmm} if HAS_OPENMM else {}

from paths_cli.wizard.errors import FILE_LOADING_ERROR_MSG, not_installed
from paths_cli.wizard.core import get_object

# should be able to simplify this try block when we drop OpenMM < 7.6
from paths_cli.compat.openmm import mm, HAS_OPENMM

OPENMM_SERIALIZATION_URL=(
    "http://docs.openmm.org/latest/api-python/generated/"
    "openmm.openmm.XmlSerializer.html"
)

from paths_cli.wizard.parameters import (
    SimpleParameter, InstanceBuilder, load_custom_eval, CUSTOM_EVAL_ERROR
)

### TOPOLOGY

def _topology_loader(filename):
    import openpathsampling as paths
    return paths.engines.openmm.snapshot_from_pdb(filename).topology

topology_parameter = SimpleParameter(
    name='topology',
    ask="Where is a PDB file describing your system?",
    loader=_topology_loader,
    helper=None,  # TODO
    error=FILE_LOADING_ERROR_MSG,
)

### INTEGRATOR/SYSTEM (XML FILES)

_where_is_xml = "Where is the XML file for your OpenMM {obj_type}?"
_xml_help = (
    "You can write OpenMM objects like systems and integrators to XML "
    "files using the XMLSerializer class. Learn more here:\n"
    "http://docs.openmm.org/latest/api-python/generated/"
    "simtk.openmm.openmm.XmlSerializer.html"
)
# TODO: switch to using load_openmm_xml from input file setup
def _openmm_xml_loader(xml):
    with open(xml, 'r') as xml_f:
        data = xml_f.read()
    return mm.XmlSerializer.deserialize(data)

integrator_parameter = SimpleParameter(
    name='integrator',
    ask=_where_is_xml.format(obj_type='integrator'),
    loader=_openmm_xml_loader,
    helper=_xml_help,
    error=FILE_LOADING_ERROR_MSG
)

system_parameter = SimpleParameter(
    name='system',
    ask=_where_is_xml.format(obj_type='system'),
    loader=_openmm_xml_loader,
    helper=_xml_help,
    error=FILE_LOADING_ERROR_MSG
)

# these two are generic, and should be kept somewhere where they can be
# reused
n_steps_per_frame_parameter = SimpleParameter(
    name="n_steps_per_frame",
    ask="How many MD steps per saved frame?",
    loader=load_custom_eval(int),
    error=CUSTOM_EVAL_ERROR,
)

n_frames_max_parameter = SimpleParameter(
    name='n_frames_max',
    ask="How many frames before aborting a trajectory?",
    loader=load_custom_eval(int),
    error=CUSTOM_EVAL_ERROR,
)

# this is taken directly from the input files setup; should find a universal
# place for this (and probably other loaders)
def openmm_options(dct):
    n_steps_per_frame = dct.pop('n_steps_per_frame')
    n_frames_max = dct.pop('n_frames_max')
    options = {'n_steps_per_frame': n_steps_per_frame,
               'n_frames_max': n_frames_max}
    dct['options'] = options
    return dct

openmm_builder = InstanceBuilder(
    parameters=[
        topology_parameter,
        system_parameter,
        integrator_parameter,
        n_steps_per_frame_parameter,
        n_frames_max_parameter,
    ],
    category='engine',
    cls='openpathsampling.engines.openmm.Engine',
    intro="You're doing an OpenMM engine",
    help_str=None,
    remapper=openmm_options
)



#####################################################################

def _openmm_serialization_helper(wizard, user_input):  # no-cov
    wizard.say("You can write OpenMM objects like systems and integrators "
               "to XML files using the XMLSerializer class. Learn more "
               f"here: \n{OPENMM_SERIALIZATION_URL}")


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
    if not HAS_OPENMM:  # no-cov
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

SUPPORTED = {"OpenMM": openmm_builder} if HAS_OPENMM else {}

if __name__ == "__main__":
    from paths_cli.wizard.wizard import Wizard
    wizard = Wizard([])
    engine = openmm_builder(wizard)
    print(engine)

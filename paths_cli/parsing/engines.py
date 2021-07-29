from .topology import build_topology
from .core import Parser, InstanceBuilder, custom_eval, Builder
from paths_cli.parsing.core import Parameter
from .tools import custom_eval_int
from paths_cli.parsing.plugins import EngineParserPlugin

from paths_cli.errors import MissingIntegrationError

try:
    from simtk import openmm as mm
except ImportError:
    HAS_OPENMM = False
else:
    HAS_OPENMM = True

def load_openmm_xml(filename):
    if not HAS_OPENMM:  # pragma: no cover
        raise RuntimeError("OpenMM does not seem to be installed")

    with open(filename, mode='r') as f:
        obj = mm.XmlSerializer.deserialize(f.read())

    return obj

def openmm_options(dct):
    n_steps_per_frame = dct.pop('n_steps_per_frame')
    n_frames_max = dct.pop('n_frames_max')
    options = {'n_steps_per_frame': n_steps_per_frame,
               'n_frames_max': n_frames_max}
    dct['options'] = options
    return dct


OPENMM_PARAMETERS = [
    Parameter('topology', build_topology, json_type='string',
              description=("File describing the topoplogy of this system; "
                           "PDB recommended")),
    Parameter('system', load_openmm_xml, json_type='string',
              description="XML file with the OpenMM system"),
    Parameter('integrator', load_openmm_xml, json_type='string',
              description="XML file with the OpenMM integrator"),
    Parameter('n_steps_per_frame', custom_eval_int,
              description="number of MD steps per saved frame"),
    Parameter("n_frames_max", custom_eval_int,
              description=("maximum number of frames before aborting "
                           "trajectory")),
]

OPENMM_PLUGIN = EngineParserPlugin(
    builder=Builder('openpathsampling.engines.openmm.Engine',
                    remapper=openmm_options),
    parameters=OPENMM_PARAMETERS,
    name='openmm',
)

TYPE_MAPPING = {
    'openmm': OPENMM_PLUGIN,
}

engine_parser = Parser(TYPE_MAPPING, label="engines")

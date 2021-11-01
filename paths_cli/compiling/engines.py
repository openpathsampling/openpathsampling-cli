from paths_cli.compiling.topology import build_topology
from paths_cli.compiling.core import Builder
from paths_cli.compiling.core import Parameter
from paths_cli.compiling.tools import custom_eval_int_strict_pos
from paths_cli.compiling.plugins import EngineCompilerPlugin, CategoryPlugin


def load_openmm_xml(filename):
    from paths_cli.compat.openmm import HAS_OPENMM, mm
    if not HAS_OPENMM:  # -no-cov-
        raise RuntimeError("OpenMM does not seem to be installed")

    with open(filename, mode='r') as f:
        obj = mm.XmlSerializer.deserialize(f.read())

    return obj


def _openmm_options(dct):
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
    Parameter('n_steps_per_frame', custom_eval_int_strict_pos,
              description="number of MD steps per saved frame"),
    Parameter("n_frames_max", custom_eval_int_strict_pos,
              description=("maximum number of frames before aborting "
                           "trajectory")),
]

OPENMM_PLUGIN = EngineCompilerPlugin(
    builder=Builder('openpathsampling.engines.openmm.Engine',
                    remapper=_openmm_options),
    parameters=OPENMM_PARAMETERS,
    name='openmm',
)

ENGINE_COMPILER = CategoryPlugin(EngineCompilerPlugin, aliases=['engines'])

from .topology import build_topology
from .core import Parser, InstanceBuilder, custom_eval

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


OPENMM_ATTRS = {
    'topology': build_topology,
    'system': load_openmm_xml,
    'integrator': load_openmm_xml,
    'n_steps_per_frame': int,
    'n_frames_max': int,
}

build_openmm_engine = InstanceBuilder(
    module='openpathsampling.engines.openmm',
    builder='Engine',
    attribute_table=OPENMM_ATTRS,
    remapper=openmm_options
)

TYPE_MAPPING = {
    'openmm': build_openmm_engine,
}

engine_parser = Parser(TYPE_MAPPING, label="engine")

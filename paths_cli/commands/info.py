import click

import importlib

def get_module_version(module_name, version_path="version.full_version"):
    try:
        mod = importlib.import_module(module_name)
    except ImportError:
        return "NOT INSTALLED"
    attr_seq = version_path.split('.')
    current = mod
    for attr in attr_seq:
        current = getattr(current, attr)
    return current

LABEL_TO_MODULE = {
    'OpenPathSampling': 'openpathsampling',
    'OpenPathSampling CLI': 'paths_cli',
    'OpenMM': 'simtk.openmm'
}

NONDEFAULT_VERSION_PATHS = {
}

def python_module_info(label):
    module = LABEL_TO_MODULE[label]
    try:
        version_path = NONDEFAULT_VERSION_PATHS[label]
    except KeyError:
        version_path = 'version.full_version'
    version = get_module_version(module, version_path)
    return label, version

FORMAT = "{label}: {version}"

@click.command(
    'info',
    short_help="Environment information",
)
def info():
    OPS_LABELS = ['OpenPathSampling', 'OpenPathSampling CLI']
    OPENMM_LABELS = ['OpenMM']

    for label in OPS_LABELS:
        label, version = python_module_info(label)
        print(FORMAT.format(label=label, version=version))


CLI = info
SECTION = "Miscellaneous"
REQUIRES_OPS = (1, 0)

import os
import importlib

from .core import Parser, InstanceBuilder, custom_eval
from .topology import build_topology
from .errors import InputError


class AllowedPackageHandler:
    def __init__(self, package):
        self.package = package

    def __call__(self, source):
        try:
            pkg = importlib.import_module(self.package)
            func = getattr(pkg, source)
        except AttributeError:
            raise InputError(f"No function called {source} in {self.package}")
        # on ImportError, we leave the error unchanged
        return func

def cv_prepare_dict(dct):
    kwargs = dct.pop('kwargs', {})
    dct.update(kwargs)
    return dct

# MDTraj-specific

mdtraj_source = AllowedPackageHandler("mdtraj")
MDTRAJ_ATTRS = {
    'topology': build_topology,
    'func': mdtraj_source,
    'kwargs': lambda kwargs: {key: custom_eval(arg)
                              for key, arg in kwargs.items()},
}

MDTRAJ_SCHEMA = {
    'topology': {
        'type': 'string',
        'description': 'topology from file or engine name',
    },
    'func': {
        'type': 'string',
        'description': 'MDTraj function, e.g., ``compute_distances``',
    },
    'kwargs': {
        'type': 'object',
        'description': 'keyword arguments for ``func``',
    },
}

build_mdtraj_function_cv = InstanceBuilder(
    module='openpathsampling.experimental.storage.collective_variables',
    builder='MDTrajFunctionCV',
    attribute_table=MDTRAJ_ATTRS,
    remapper = cv_prepare_dict,
)

# Mock for integration testing
def mock_cv_builder(dct):
    from mock import Mock
    from openpathsampling.experimental.storage.collective_varibles import \
            FunctionCV
    mock = Mock(return_value=dct['return_value'])
    return FunctionCV(mock)



# Main CV parser

TYPE_MAPPING = {
    'mdtraj': build_mdtraj_function_cv,
}

cv_parser = Parser(TYPE_MAPPING, label="CV")

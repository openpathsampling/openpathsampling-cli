import os
import importlib

from .core import Parser, InstanceBuilder, custom_eval, Parameter
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
# MDTRAJ_ATTRS = {
    # 'topology': build_topology,
    # 'func': mdtraj_source,
    # 'kwargs': lambda kwargs: {key: custom_eval(arg)
                              # for key, arg in kwargs.items()},
# }

MDTRAJ_PARAMETERS = [
    Parameter('topology', build_topology),
    Parameter('func', mdtraj_source, json_type='string',
              description="MDTraj function, e.g., ``compute_distances``"),
    Parameter('kwargs', lambda kwargs: {key: custom_eval(arg)
                                        for key, arg in kwargs.items()},
              json_type='object',
              description="keyword arguments for ``func``",
              required=True),  # TODO: bug in current: shoudl be req=False
]

build_mdtraj_function_cv = InstanceBuilder(
    attribute_table=None,  # temp
    module='openpathsampling.experimental.storage.collective_variables',
    builder='MDTrajFunctionCV',
    # attribute_table=MDTRAJ_ATTRS,
    parameters=MDTRAJ_PARAMETERS,
    remapper=cv_prepare_dict,
)

# TODO: this should replace TYPE_MAPPING and cv_parser
# MDTRAJ_PLUGIN = CVParserPlugin(
    # type_name='mdtraj',
    # instance_builder=build_mdtraj_function_cv,
    # requires_ops=(1, 0),
    # requires_cli=(0, 4),
# )


# Main CV parser

TYPE_MAPPING = {
    'mdtraj': build_mdtraj_function_cv,
}

cv_parser = Parser(TYPE_MAPPING, label="CVs")

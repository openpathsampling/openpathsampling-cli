import os
import importlib

from .core import Compiler, InstanceBuilder, custom_eval, Parameter, Builder
from .topology import build_topology
from .errors import InputError
from paths_cli.utils import import_thing
from paths_cli.compiling.plugins import CVCompilerPlugin, CompilerPlugin


class AllowedPackageHandler:
    def __init__(self, package):
        self.package = package

    def __call__(self, source):
        try:
            func = import_thing(self.package, source)
        except AttributeError:
            raise InputError(f"No function called {source} in {self.package}")
        # on ImportError, we leave the error unchanged
        return func

def cv_kwargs_remapper(dct):
    kwargs = dct.pop('kwargs', {})
    dct.update(kwargs)
    return dct


# MDTraj-specific
MDTRAJ_CV_PLUGIN = CVCompilerPlugin(
    builder=Builder('openpathsampling.experimental.storage.'
                    'collective_variables.MDTrajFunctionCV',
                    remapper=cv_kwargs_remapper),
    parameters=[
        Parameter('topology', build_topology),
        Parameter('func', AllowedPackageHandler('mdtraj'),
                  json_type='string', description="MDTraj function, e.g., "
                  "``compute_distances``"),
        Parameter('kwargs', lambda kwargs: {key: custom_eval(arg)
                                            for key, arg in kwargs.items()},
                  json_type='object', default=None,
                  description="keyword arguments for ``func``"),
        Parameter('period_min', custom_eval, default=None,
                  description=("minimum value for a periodic function, "
                               "None if not periodic")),
        Parameter('period_max', custom_eval, default=None,
                  description=("maximum value for a periodic function, "
                               "None if not periodic")),

    ],
    name="mdtraj"
)

# Main CV compiler

TYPE_MAPPING = {
    'mdtraj': MDTRAJ_CV_PLUGIN,
}

CV_COMPILER = CompilerPlugin(CVCompilerPlugin, aliases=['cvs'])
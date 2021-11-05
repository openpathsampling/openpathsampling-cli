from paths_cli.compiling.core import Parameter, Builder
from paths_cli.compiling.tools import custom_eval, custom_eval_float
from paths_cli.compiling.topology import build_topology
from paths_cli.compiling.errors import InputError
from paths_cli.utils import import_thing
from paths_cli.compiling.plugins import CVCompilerPlugin, CategoryPlugin
from paths_cli.compiling.json_type import json_type_eval


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


def _cv_kwargs_remapper(dct):
    kwargs = dct.pop('kwargs', {})
    dct.update(kwargs)
    return dct


# MDTraj-specific
MDTRAJ_CV_PLUGIN = CVCompilerPlugin(
    builder=Builder('openpathsampling.experimental.storage.'
                    'collective_variables.MDTrajFunctionCV',
                    remapper=_cv_kwargs_remapper),
    parameters=[
        Parameter('topology', build_topology),
        Parameter('func', AllowedPackageHandler('mdtraj'),
                  json_type='string', description="MDTraj function, e.g., "
                  "``compute_distances``"),
        Parameter('kwargs', lambda kwargs: {key: custom_eval(arg)
                                            for key, arg in kwargs.items()},
                  json_type='object', default=None,
                  description="keyword arguments for ``func``"),
        Parameter('period_min', custom_eval_float, default=None,
                  json_type=json_type_eval('Float'),
                  description=("minimum value for a periodic function, "
                               "None if not periodic")),
        Parameter('period_max', custom_eval_float, default=None,
                  json_type=json_type_eval('Float'),
                  description=("maximum value for a periodic function, "
                               "None if not periodic")),

    ],
    description="Use an MDTraj analysis function to calculate a CV.",
    name="mdtraj"
)

# Main CV compiler

TYPE_MAPPING = {
    'mdtraj': MDTRAJ_CV_PLUGIN,
}

CV_COMPILER = CategoryPlugin(CVCompilerPlugin, aliases=['cvs'])

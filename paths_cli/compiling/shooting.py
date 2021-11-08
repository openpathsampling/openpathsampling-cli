from paths_cli.compiling.core import (
    InstanceCompilerPlugin, CategoryCompiler, Builder, Parameter
)
from paths_cli.compiling.root_compiler import compiler_for
from paths_cli.compiling.tools import custom_eval_float
from paths_cli.compiling.plugins import ShootingPointSelectorPlugin
from paths_cli.compiling.json_type import json_type_ref, json_type_eval

shooting_selector_compiler = compiler_for('shooting-point-selector')
SP_SELECTOR_PARAMETER = Parameter(
    'selector', compiler_for('shooting-point-selector'), default=None,
    json_type=json_type_ref('shooting-point-selector'),
    description="shooting point selection algorithm to use.",
)


build_uniform_selector = ShootingPointSelectorPlugin(
    builder=Builder('openpathsampling.UniformSelector'),
    parameters=[],
    name='uniform',
    description=("Uniform shooting point selection probability: all frames "
                 "have equal probability (endpoints excluded)."),
)


def _remapping_gaussian_stddev(dct):
    dct['alpha'] = 0.5 / dct.pop('stddev')**2
    dct['collectivevariable'] = dct.pop('cv')
    dct['l_0'] = dct.pop('mean')
    return dct


build_gaussian_selector = ShootingPointSelectorPlugin(
    builder=Builder('openpathsampling.GaussianBiasSelector',
                    remapper=_remapping_gaussian_stddev),
    parameters=[
        Parameter('cv', compiler_for('cv'), json_type=json_type_ref('cv'),
                  description="bias as a Gaussian in this CV"),
        Parameter('mean', custom_eval_float,
                  json_type=json_type_eval("Float"),
                  description="mean of the Gaussian"),
        Parameter('stddev', custom_eval_float,
                  json_type=json_type_eval("Float"),
                  description="standard deviation of the Gaussian"),
    ],
    name='gaussian',
    description=(
        "Bias shooting point selection based on a Gaussian. That is, for a "
        "configuration :math:`x`, the probability of selecting that "
        "configruation is proportional to "
        r":math:`\exp(-(\lambda(x)-\bar{\lambda})^2 / (2\sigma^2))`, "
        r"where :math:`\lambda` is the given CV, :math:`\bar{\lambda}` is "
        r"the mean, and :math:`\sigma` is the standard deviation."
    ),
)



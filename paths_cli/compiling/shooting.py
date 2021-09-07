from paths_cli.compiling.core import (
    InstanceBuilder, Compiler, Builder, Parameter
)
from paths_cli.compiling.root_compiler import compiler_for
from paths_cli.compiling.tools import custom_eval
import numpy as np

build_uniform_selector = InstanceBuilder(
    builder=Builder('openpathsampling.UniformSelector'),
    parameters=[],
    name='uniform',
)

def remapping_gaussian_stddev(dct):
    dct['alpha'] = 0.5 / dct.pop('stddev')**2
    dct['collectivevariable'] = dct.pop('cv')
    dct['l_0'] = dct.pop('mean')
    return dct

build_gaussian_selector = InstanceBuilder(
    builder=Builder('openpathsampling.GaussianBiasSelector',
                    remapper=remapping_gaussian_stddev),
    parameters=[
        Parameter('cv', compiler_for('cv')),
        Parameter('mean', custom_eval),
        Parameter('stddev', custom_eval),
    ],
    name='gaussian',
)

shooting_selector_compiler = Compiler(
    type_dispatch={
        'uniform': build_uniform_selector,
        'gaussian': build_gaussian_selector,
    },
    label='shooting selectors'
)

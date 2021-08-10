from paths_cli.parsing.core import (
    InstanceBuilder, Parser, Builder, Parameter
)
from paths_cli.parsing.cvs import cv_parser
from paths_cli.parsing.tools import custom_eval
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
        Parameter('cv', cv_parser),
        Parameter('mean', custom_eval),
        Parameter('stddev', custom_eval),
    ],
    name='gaussian',
)

shooting_selector_parser = Parser(
    type_dispatch={
        'uniform': build_uniform_selector,
        'gaussian': build_gaussian_selector,
    },
    label='shooting selectors'
)

from paths_cli.parsing.core import InstanceBuilder, Parser
from paths_cli.parsing.cvs import cv_parser
from paths_cli.parsing.tools import custom_eval
import numpy as np

build_uniform_selector = InstanceBuilder(
    module='openpathsampling',
    builder='UniformSelector',
    attribute_table={}
)

def remapping_gaussian_stddev(dct):
    dct['alpha'] = 0.5 / dct.pop('stddev')**2
    return dct

build_gaussian_selector = InstanceBuilder(
    module='openpathsampling',
    builder='GaussianSelector',
    attribute_table={'cv': cv_parser,
                     'mean': custom_eval,
                     'stddev': custom_eval},
    remapper=remapping_gaussian_stddev
)

shooting_selector_parser = Parser(
    type_dispatch={
        'uniform': build_uniform_selector,
        'gaussian': build_gaussian_selector,
    },
    label='shooting selectors'
)

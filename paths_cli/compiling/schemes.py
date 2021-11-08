from paths_cli.compiling.core import (
    Builder, Parameter
)
from paths_cli.compiling.tools import (
    custom_eval, custom_eval_int_strict_pos
)
from paths_cli.compiling.strategies import SP_SELECTOR_PARAMETER
from paths_cli.compiling.plugins import SchemeCompilerPlugin, CategoryPlugin
from paths_cli.compiling.root_compiler import compiler_for
from paths_cli.compiling.json_type import (
    json_type_ref, json_type_list, json_type_eval
)


NETWORK_PARAMETER = Parameter(
    'network',
    compiler_for('network'),
    json_type=json_type_ref('network'),
    description="network to use with this scheme"
)

ENGINE_PARAMETER = Parameter(
    'engine', compiler_for('engine'),
    json_type=json_type_ref('engine'),
    description="engine to use with this scheme",
)  # reuse?

STRATEGIES_PARAMETER = Parameter('strategies', compiler_for('strategy'),
                                 json_type=json_type_ref('strategy'),
                                 default=None)


SPRING_SHOOTING_PLUGIN = SchemeCompilerPlugin(
    builder=Builder('openpathsampling.SpringShootingMoveScheme'),
    parameters=[
        NETWORK_PARAMETER,
        Parameter('k_spring', custom_eval,
                  json_type=json_type_eval("Float"),
                  description="spring constant for the spring shooting move"),
        Parameter('delta_max', custom_eval_int_strict_pos,
                  json_type=json_type_eval("IntStrictPos"),
                  description=("maximum shift in shooting point (number of "
                               "frames)"),
                  ),
        ENGINE_PARAMETER
    ],
    name='spring-shooting',
    description=("Move scheme for TPS with the spring-shooting algorithm. "
                 "Under most circumstances, the network provided here "
                 "should be a 2-state TPS network."),
)


class BuildSchemeStrategy:
    def __init__(self, scheme_class, default_global_strategy):
        self.scheme_class = scheme_class
        self.default_global_strategy = default_global_strategy

    def __call__(self, **dct):
        from openpathsampling import strategies
        if self.default_global_strategy:
            global_strategy = [strategies.OrganizeByMoveGroupStrategy()]
        else:
            global_strategy = []

        builder = Builder(self.scheme_class)
        strategies = global_strategy + dct.pop('strategies', [])
        scheme = builder(**dct)
        for strat in strategies:
            scheme.append(strat)
        return scheme


ONE_WAY_SHOOTING_SCHEME_PLUGIN = SchemeCompilerPlugin(
    builder=BuildSchemeStrategy('openpathsampling.OneWayShootingMoveScheme',
                                default_global_strategy=False),
    parameters=[
        NETWORK_PARAMETER,
        SP_SELECTOR_PARAMETER,
        ENGINE_PARAMETER,
        STRATEGIES_PARAMETER,
    ],
    name='one-way-shooting',
    description=("One-way-shooting move scheme. This can be extended with "
                 "additional user-defined move strategies."),
)

MOVESCHEME_PLUGIN = SchemeCompilerPlugin(
    builder=BuildSchemeStrategy('openpathsampling.MoveScheme',
                                default_global_strategy=True),
    parameters=[
        NETWORK_PARAMETER,
        STRATEGIES_PARAMETER,
    ],
    name='scheme',
    description=("Generic move scheme. Add strategies to this to make it "
                 "useful. This defaults to a scheme that first chooses a "
                 "move type, and then chooses the specific move within "
                 "that type (i.e., ``OrganizeByMoveGroupStrategy``)"),
)

SCHEME_COMPILER = CategoryPlugin(SchemeCompilerPlugin, aliases=['schemes'])

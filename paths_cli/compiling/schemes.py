from paths_cli.compiling.core import (
    InstanceBuilder, Compiler, Builder, Parameter
)
from paths_cli.compiling.tools import custom_eval
from paths_cli.compiling.shooting import shooting_selector_compiler
from paths_cli.compiling.strategies import SP_SELECTOR_PARAMETER
from paths_cli.compiling.plugins import SchemeCompilerPlugin, CompilerPlugin
from paths_cli.compiling.root_compiler import compiler_for


NETWORK_PARAMETER = Parameter('network', compiler_for('network'))

ENGINE_PARAMETER = Parameter('engine', compiler_for('engine'))  # reuse?

STRATEGIES_PARAMETER = Parameter('strategies', compiler_for('strategy'),
                                 default=None)


build_spring_shooting_scheme = SchemeCompilerPlugin(
    builder=Builder('openpathsampling.SpringShootingMoveScheme'),
    parameters=[
        NETWORK_PARAMETER,
        Parameter('k_spring', custom_eval),
        Parameter('delta_max', custom_eval),
        ENGINE_PARAMETER
    ],
    name='spring-shooting',
)

class BuildSchemeStrategy:
    def __init__(self, scheme_class, default_global_strategy):
        self.scheme_class = scheme_class
        self.default_global_strategy = default_global_strategy

    def __call__(self, dct):
        from openpathsampling import strategies
        if self.default_global_strategy:
            global_strategy = [strategies.OrganizeByMoveGroupStrategy()]
        else:
            global_strategy = []

        builder = Builder(self.scheme_class)
        strategies = dct.pop('strategies', []) + global_strategy
        scheme = builder(dct)
        for strat in strategies:
            scheme.append(strat)
        # self.logger.debug(f"strategies: {scheme.strategies}")
        return scheme


build_one_way_shooting_scheme = SchemeCompilerPlugin(
    builder=BuildSchemeStrategy('openpathsampling.OneWayShootingMoveScheme',
                                default_global_strategy=False),
    parameters=[
        NETWORK_PARAMETER,
        SP_SELECTOR_PARAMETER,
        ENGINE_PARAMETER,
        STRATEGIES_PARAMETER,
    ],
    name='one-way-shooting',
)

build_scheme = SchemeCompilerPlugin(
    builder=BuildSchemeStrategy('openpathsampling.MoveScheme',
                                default_global_strategy=True),
    parameters=[
        NETWORK_PARAMETER,
        STRATEGIES_PARAMETER,
    ],
    name='scheme'
)

SCHEME_COMPILER = CompilerPlugin(SchemeCompilerPlugin, aliases=['schemes'])

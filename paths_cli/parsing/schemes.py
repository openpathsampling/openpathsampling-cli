from paths_cli.parsing.core import (
    InstanceBuilder, Parser, Builder, Parameter
)
from paths_cli.parsing.tools import custom_eval
from paths_cli.parsing.shooting import shooting_selector_parser
from paths_cli.parsing.networks import network_parser
from paths_cli.parsing.strategies import (
    strategy_parser, SP_SELECTOR_PARAMETER
)
from paths_cli.parsing.plugins import SchemeParserPlugin, ParserPlugin
from paths_cli.parsing.root_parser import parser_for


NETWORK_PARAMETER = Parameter('network', network_parser)

ENGINE_PARAMETER = Parameter('engine', parser_for('engine'))  # reuse elsewhere?

STRATEGIES_PARAMETER = Parameter('strategies', strategy_parser, default=None)


build_spring_shooting_scheme = SchemeParserPlugin(
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


build_one_way_shooting_scheme = SchemeParserPlugin(
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

build_scheme = SchemeParserPlugin(
    builder=BuildSchemeStrategy('openpathsampling.MoveScheme',
                                default_global_strategy=True),
    parameters=[
        NETWORK_PARAMETER,
        STRATEGIES_PARAMETER,
    ],
    name='scheme'
)

SCHEME_PARSER = ParserPlugin(SchemeParserPlugin, aliases=['schemes'])
scheme_parser = Parser(
    type_dispatch={
        'one-way-shooting': build_one_way_shooting_scheme,
        'spring-shooting': build_spring_shooting_scheme,
        'scheme': build_scheme,
        'default-tis': ...,
    },
    label='move schemes'
)


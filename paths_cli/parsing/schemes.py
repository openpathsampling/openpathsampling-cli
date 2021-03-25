from paths_cli.parsing.core import InstanceBuilder, Parser
from paths_cli.parsing.tools import custom_eval
from paths_cli.parsing.shooting import shooting_selector_parser
from paths_cli.parsing.engines import engine_parser
from paths_cli.parsing.networks import network_parser
from paths_cli.parsing.strategies import strategy_parser

build_spring_shooting_scheme = InstanceBuilder(
    module='openpathsampling',
    builder='SpringShootingMoveScheme',
    attribute_table={
        'network': network_parser,
        'k_spring': custom_eval,
        'delta_max': custom_eval,
        'engine': engine_parser,
    }
)

class StrategySchemeInstanceBuilder(InstanceBuilder):
    """
    Variant of the InstanceBuilder that appends strategies to a MoveScheme
    """
    def __init__(self, builder, attribute_table, defaults=None, module=None,
                 remapper=None, default_global_strategy=False):
        from openpathsampling import strategies
        super().__init__(builder, attribute_table, defaults=defaults,
                         module=module, remapper=remapper)
        if default_global_strategy is True:
            self.default_global = [strategies.OrganizeByMoveGroupStrategy()]
        elif default_global_strategy is False:
            self.default_global = []
        else:
            self.default_global= [default_global_strategy]

    def __call__(self, dct):
        new_dct = self._parse_attrs(dct)
        strategies = new_dct.pop('strategies')
        scheme = self._build(new_dct)
        for strat in strategies + self.default_global:
            scheme.append(strat)

        self.logger.debug(f"strategies: {scheme.strategies}")
        return scheme


build_one_way_shooting_scheme = StrategySchemeInstanceBuilder(
    module='openpathsampling',
    builder='OneWayShootingMoveScheme',
    attribute_table={
        'network': network_parser,
        'selector': shooting_selector_parser,
        'engine': engine_parser,
        'strategies': strategy_parser,
    }
)

build_scheme = StrategySchemeInstanceBuilder(
    module='openpathsampling',
    builder='MoveScheme',
    attribute_table={
        'network': network_parser,
        'strategies': strategy_parser,
    },
    default_global_strategy=True,
)

scheme_parser = Parser(
    type_dispatch={
        'one-way-shooting': build_one_way_shooting_scheme,
        'spring-shooting': build_spring_shooting_scheme,
        'scheme': build_scheme,
        'default-tis': ...,
    },
    label='movescheme'
)


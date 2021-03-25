from paths_cli.parsing.core import InstanceBuilder, Parser
from paths_cli.parsing.shooting import shooting_selector_parser
from paths_cli.parsing.engines import engine_parser

build_one_way_shooting_strategy = InstanceBuilder(
    module='openpathsampling.strategies',
    builder='OneWayShootingStrategy',
    attribute_table={
        'selector': shooting_selector_parser,
        'engine': engine_parser,
    },
    optional_attributes={
        'group': str,
        'replace': bool,
    }
)

build_two_way_shooting_strategy = InstanceBuilder(
    module='openpathsampling.strategies',
    builder='TwoWayShootingStrategy',
    attribute_table={
        'modifier': ...,
        'selector': shooting_selector_parser,
        'engine': engine_parser,
    },
    optional_attributes={
        'group': str,
        'replace': bool,
    }
)

build_nearest_neighbor_repex_strategy = InstanceBuilder(
    module='openpathsampling.strategies',
    builder='NearestNeighborRepExStrategy',
    attribute_table={},
    optional_attributes={
        'group': str,
        'replace': bool,
    },
)

build_all_set_repex_strategy = InstanceBuilder(
    module='openpathsampling.strategies',
    builder='AllSetRepExStrategy',
    attribute_table={},
    optional_attributes={
        'group': str,
        'replace': bool,
    }
)

build_path_reversal_strategy = InstanceBuilder(
    module='openpathsampling.strategies',
    builder='PathReversalStrategy',
    attribute_table={},
    optional_attributes={
        'group': str,
        'replace': bool,
    }
)

build_minus_move_strategy = InstanceBuilder(
    module='openpathsampling.strategies',
    builder='MinusMoveStrategy',
    attribute_table={
        'engine': engine_parser,
    },
    optional_attributes={
        'group': str,
        'replace': bool,
    }
)

build_single_replica_minus_move_strategy = InstanceBuilder(
    module='openpathsampling.strategies',
    builder='SingleReplicaMinusMoveStrategy',
    attribute_table={
        'engine': engine_parser,
    },
    optional_attributes={
        'group': str,
        'replace': bool,
    }
)

strategy_parser = Parser(
    type_dispatch={
        'one-way-shooting': build_one_way_shooting_strategy,
        'two-way-shooting': build_two_way_shooting_strategy,
        'nearest-neighbor-repex': build_nearest_neighbor_repex_strategy,
        'all-set-repex': build_all_set_repex_strategy,
        'path-reversal': build_path_reversal_strategy,
        'minus': build_minus_move_strategy,
        'single-rep-minux': build_single_replica_minus_move_strategy,
    },
    label="strategy"
)

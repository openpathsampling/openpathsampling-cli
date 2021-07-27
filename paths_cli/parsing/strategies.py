from paths_cli.parsing.core import (
    InstanceBuilder, Parser, Builder, Parameter
)
from paths_cli.parsing.shooting import shooting_selector_parser
from paths_cli.parsing.engines import engine_parser

def _strategy_name(class_name):
    return f"openpathsampling.strategies.{class_name}"

def _group_parameter(group_name):
    return Parameter('group', str, default=group_name,
                     description="the group name for these movers")

# TODO: maybe this moves into shooting once we have the metadata?
SP_SELECTOR_PARAMETER = Parameter('selector', shooting_selector_parser)

ENGINE_PARAMETER = Parameter('engine', engine_parser,
                             description="the engine for moves of this "
                             "type")

SHOOTING_GROUP_PARAMETER = _group_parameter('shooting')
REPEX_GROUP_PARAMETER = _group_parameter('repex')
MINUS_GROUP_PARAMETER = _group_parameter('minus')

REPLACE_TRUE_PARAMETER = Parameter('replace', bool, default=True)
REPLACE_FALSE_PARAMETER = Parameter('replace', bool, default=False)



build_one_way_shooting_strategy = InstanceBuilder(
    builder=Builder(_strategy_name("OneWayShootingStrategy")),
    parameters=[
        SP_SELECTOR_PARAMETER,
        ENGINE_PARAMETER,
        SHOOTING_GROUP_PARAMETER,
        Parameter('replace', bool, default=True)
    ],
)

build_two_way_shooting_strategy = InstanceBuilder(
    builder=Builder(_strategy_name("TwoWayShootingStrategy")),
    parameters = [
        Parameter('modifier', ...),
        SP_SELECTOR_PARAMETER,
        ENGINE_PARAMETER,
        SHOOTING_GROUP_PARAMETER,
        REPLACE_TRUE_PARAMETER,
    ],
)

build_nearest_neighbor_repex_strategy = InstanceBuilder(
    builder=Builder(_strategy_name("NearestNeighborRepExStrategy")),
    parameters=[
        REPEX_GROUP_PARAMETER,
        REPLACE_TRUE_PARAMETER
    ],
)

build_all_set_repex_strategy = InstanceBuilder(
    builder=Builder(_strategy_name("AllSetRepExStrategy")),
    parameters=[
        REPEX_GROUP_PARAMETER,
        REPLACE_TRUE_PARAMETER
    ],
)

build_path_reversal_strategy = InstanceBuilder(
    builder=Builder(_strategy_name("PathReversalStrategy")),
    parameters=[
        _group_parameter('pathreversal'),
        REPLACE_TRUE_PARAMETER,
    ]
)

build_minus_move_strategy = InstanceBuilder(
    builder=Builder(_strategy_name("MinusMoveStrategy")),
    parameters=[
        ENGINE_PARAMETER,
        MINUS_GROUP_PARAMETER,
        REPLACE_TRUE_PARAMETER,
    ],
)

build_single_replica_minus_move_strategy = InstanceBuilder(
    builder=Builder(_strategy_name("SingleReplicaMinusMoveStrategy")),
    parameters=[
        ENGINE_PARAMETER,
        MINUS_GROUP_PARAMETER,
        REPLACE_TRUE_PARAMETER,
    ],
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

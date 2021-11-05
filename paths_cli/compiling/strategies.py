from paths_cli.compiling.core import Builder, Parameter
# from paths_cli.compiling.shooting import shooting_selector_compiler
from paths_cli.compiling.plugins import (
    StrategyCompilerPlugin, CategoryPlugin
)
from paths_cli.compiling.root_compiler import compiler_for
from paths_cli.compiling.json_type import json_type_ref

shooting_selector_compiler = compiler_for('shooting-point-selector')


def _strategy_name(class_name):
    return f"openpathsampling.strategies.{class_name}"


def _group_parameter(group_name):
    return Parameter('group', str, json_type="string", default=group_name,
                     description="the group name for these movers")


# TODO: maybe this moves into shooting once we have the metadata?
SP_SELECTOR_PARAMETER = Parameter('selector', shooting_selector_compiler,
                                  default=None)

ENGINE_PARAMETER = Parameter(
    'engine', compiler_for('engine'), json_type=json_type_ref('engine'),
    description="the engine for moves of this type"
)

SHOOTING_GROUP_PARAMETER = _group_parameter('shooting')
REPEX_GROUP_PARAMETER = _group_parameter('repex')
MINUS_GROUP_PARAMETER = _group_parameter('minus')

REPLACE_TRUE_PARAMETER = Parameter(
    'replace', bool, json_type="bool", default=True,
    description=("whether this should replace existing objects (default "
                 "True)")
)
REPLACE_FALSE_PARAMETER = Parameter(
    'replace', bool, json_type="bool", default=False,
    description=("whether this should replace existing objects (default "
                 "False)")
)


ONE_WAY_SHOOTING_STRATEGY_PLUGIN = StrategyCompilerPlugin(
    builder=Builder(_strategy_name("OneWayShootingStrategy")),
    parameters=[
        SP_SELECTOR_PARAMETER,
        ENGINE_PARAMETER,
        SHOOTING_GROUP_PARAMETER,
        REPLACE_TRUE_PARAMETER
    ],
    name='one-way-shooting',
)
build_one_way_shooting_strategy = ONE_WAY_SHOOTING_STRATEGY_PLUGIN

# build_two_way_shooting_strategy = StrategyCompilerPlugin(
#     builder=Builder(_strategy_name("TwoWayShootingStrategy")),
#     parameters = [
#         Parameter('modifier', ...),
#         SP_SELECTOR_PARAMETER,
#         ENGINE_PARAMETER,
#         SHOOTING_GROUP_PARAMETER,
#         REPLACE_TRUE_PARAMETER,
#     ],
#     name='two-way-shooting',
# )

build_nearest_neighbor_repex_strategy = StrategyCompilerPlugin(
    builder=Builder(_strategy_name("NearestNeighborRepExStrategy")),
    parameters=[
        REPEX_GROUP_PARAMETER,
        REPLACE_TRUE_PARAMETER
    ],
    name='nearest-neighbor-repex',
)

build_all_set_repex_strategy = StrategyCompilerPlugin(
    builder=Builder(_strategy_name("AllSetRepExStrategy")),
    parameters=[
        REPEX_GROUP_PARAMETER,
        REPLACE_TRUE_PARAMETER
    ],
    name='all-set-repex',
)

build_path_reversal_strategy = StrategyCompilerPlugin(
    builder=Builder(_strategy_name("PathReversalStrategy")),
    parameters=[
        _group_parameter('pathreversal'),
        REPLACE_TRUE_PARAMETER,
    ],
    name='path-reversal',
)

build_minus_move_strategy = StrategyCompilerPlugin(
    builder=Builder(_strategy_name("MinusMoveStrategy")),
    parameters=[
        ENGINE_PARAMETER,
        MINUS_GROUP_PARAMETER,
        REPLACE_TRUE_PARAMETER,
    ],
    name='minus',
)

build_single_replica_minus_move_strategy = StrategyCompilerPlugin(
    builder=Builder(_strategy_name("SingleReplicaMinusMoveStrategy")),
    parameters=[
        ENGINE_PARAMETER,
        MINUS_GROUP_PARAMETER,
        REPLACE_TRUE_PARAMETER,
    ],
    name='single-replica-minus',
)

STRATEGY_COMPILER = CategoryPlugin(StrategyCompilerPlugin,
                                   aliases=['strategies'])

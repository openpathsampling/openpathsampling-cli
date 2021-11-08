from paths_cli.compiling.core import (
    InstanceCompilerPlugin, Builder, Parameter
)
from paths_cli.compiling.tools import custom_eval
from paths_cli.compiling.plugins import (
    NetworkCompilerPlugin, CategoryPlugin, InterfaceSetPlugin
)
from paths_cli.compiling.root_compiler import compiler_for
from paths_cli.compiling.json_type import (
    json_type_ref, json_type_list, json_type_eval
)


INITIAL_STATES_PARAM = Parameter(
    'initial_states', compiler_for('volume'),
    json_type=json_type_list(json_type_ref('volume')),
    description="initial states for this transition",
)


INITIAL_STATE_PARAM = Parameter(
    'initial_state', compiler_for('volume'),
    json_type=json_type_list(json_type_ref('volume')),
    description="initial state for this transition",
)


FINAL_STATES_PARAM = Parameter(
    'final_states', compiler_for('volume'),
    json_type=json_type_list(json_type_ref('volume')),
    description="final states for this transition",
)


FINAL_STATE_PARAM = Parameter(
    'final_state', compiler_for('volume'),
    json_type=json_type_list(json_type_ref('volume')),
    description="final state for this transition",
)


build_interface_set = InterfaceSetPlugin(
    builder=Builder('openpathsampling.VolumeInterfaceSet'),
    parameters=[
        Parameter('cv', compiler_for('cv'), json_type=json_type_ref('cv'),
                  description=("the collective variable for this interface "
                               "set")),
        Parameter('minvals', custom_eval,
                  json_type=json_type_list(json_type_eval("Float")),
                  description=("minimum value(s) for interfaces in this"
                               "interface set")),
        Parameter('maxvals', custom_eval,
                  json_type=json_type_list(json_type_eval("Float")),
                  description=("maximum value(s) for interfaces in this"
                               "interface set")),
    ],
    name='interface-set',
    description="Interface set used in transition interface sampling.",
)


def mistis_trans_info(dct):
    dct = dct.copy()
    transitions = dct.pop('transitions')
    volume_compiler = compiler_for('volume')
    trans_info = [
        (
            volume_compiler(trans['initial_state']),
            build_interface_set(trans['interfaces']),
            volume_compiler(trans['final_state'])
        )
        for trans in transitions
    ]
    dct['trans_info'] = trans_info
    return dct


def tis_trans_info(dct):
    # remap TIS into MISTIS format
    dct = dct.copy()
    initial_state = dct.pop('initial_state')
    final_state = dct.pop('final_state')
    interface_set = dct.pop('interfaces')
    dct['transitions'] = [{'initial_state': initial_state,
                           'final_state': final_state,
                           'interfaces': interface_set}]
    return mistis_trans_info(dct)


TPS_NETWORK_PLUGIN = NetworkCompilerPlugin(
    builder=Builder('openpathsampling.TPSNetwork'),
    parameters=[INITIAL_STATES_PARAM, FINAL_STATES_PARAM],
    name='tps',
    description=("Network for transition path sampling (two state TPS or "
                 "multiple state TPS)."),
)


# MISTIS_NETWORK_PLUGIN = NetworkCompilerPlugin(
#     parameters=[Parameter('trans_info', mistis_trans_info)],
#     builder=Builder('openpathsampling.MISTISNetwork'),
#     name='mistis'
# )


# TIS_NETWORK_PLUGIN = NetworkCompilerPlugin(
#     builder=Builder('openpathsampling.MISTISNetwork'),
#     parameters=[Parameter('trans_info', tis_trans_info)],
#     name='tis'
# )

# old names not yet replaced in testing  THESE ARE WHY WE'RE DOUBLING! GET
# RID OF THEM! (also, use an is-check)
build_tps_network = TPS_NETWORK_PLUGIN


NETWORK_COMPILER = CategoryPlugin(NetworkCompilerPlugin, aliases=['networks'])

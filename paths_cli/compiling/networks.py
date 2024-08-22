from paths_cli.compiling.core import (
    InstanceCompilerPlugin, Builder, Parameter,
    listify, unlistify
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

def mistis_trans_info_param_builder(dcts):
    default = 'volume-interface-set'  # TODO: make this flexible?
    trans_info = []
    volume_compiler = compiler_for("volume")
    interface_set_compiler = compiler_for('interface_set')
    for dct in dcts:
        dct = dct.copy()
        dct['type'] = dct.get('type', default)
        initial_state = volume_compiler(dct.pop('initial_state'))
        final_state = volume_compiler(dct.pop('final_state'))
        interface_set = interface_set_compiler(dct)
        trans_info.append((initial_state, interface_set, final_state))

    return trans_info


MISTIS_INTERFACE_SETS_PARAM = Parameter(
    'interface_sets', mistis_trans_info_param_builder,
    json_type=json_type_list(json_type_ref('interface-set')),
    description='interface sets for MISTIS'
)

# this is reused in the simple single TIS setup
VOLUME_INTERFACE_SET_PARAMS = [
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
]


VOLUME_INTERFACE_SET_PLUGIN = InterfaceSetPlugin(
    builder=Builder('openpathsampling.VolumeInterfaceSet'),
    parameters=VOLUME_INTERFACE_SET_PARAMS,
    name='volume-interface-set',
    description="Interface set used in transition interface sampling.",
)


def mistis_trans_info(dct):
    dct = dct.copy()
    dct['trans_info'] = dct.pop('interface_sets')
    return dct


TPS_NETWORK_PLUGIN = NetworkCompilerPlugin(
    builder=Builder('openpathsampling.TPSNetwork'),
    parameters=[INITIAL_STATES_PARAM, FINAL_STATES_PARAM],
    name='tps',
    description=("Network for transition path sampling (two state TPS or "
                 "multiple state TPS)."),
)


MISTIS_NETWORK_PLUGIN = NetworkCompilerPlugin(
    parameters=[MISTIS_INTERFACE_SETS_PARAM],
    builder=Builder('openpathsampling.MISTISNetwork',
                    remapper=mistis_trans_info),
    name='mistis'
)

def single_tis_builder(initial_state, final_state, cv, minvals, maxvals):
    import openpathsampling as paths
    interface_set = paths.VolumeInterfaceSet(cv, minvals, maxvals)
    return paths.MISTISNetwork([
        (initial_state, interface_set, final_state)
    ])

TIS_NETWORK_PLUGIN = NetworkCompilerPlugin(
    builder=single_tis_builder,
    parameters=([INITIAL_STATE_PARAM, FINAL_STATE_PARAM]
                + VOLUME_INTERFACE_SET_PARAMS),
    name='tis'
)


# old names not yet replaced in testing  THESE ARE WHY WE'RE DOUBLING! GET
# RID OF THEM! (also, use an is-check)
build_tps_network = TPS_NETWORK_PLUGIN


NETWORK_COMPILER = CategoryPlugin(NetworkCompilerPlugin, aliases=['networks'])

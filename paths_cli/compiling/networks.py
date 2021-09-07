from paths_cli.compiling.core import (
    InstanceBuilder, Compiler, Builder, Parameter
)
from paths_cli.compiling.tools import custom_eval
from paths_cli.compiling.plugins import NetworkCompilerPlugin, CompilerPlugin
from paths_cli.compiling.root_compiler import compiler_for

build_interface_set = InstanceBuilder(
    builder=Builder('openpathsampling.VolumeInterfaceSet'),
    parameters=[
        Parameter('cv', compiler_for('cv'), description="the collective "
                  "variable for this interface set"),
        Parameter('minvals', custom_eval), # TODO fill in JSON types
        Parameter('maxvals', custom_eval), # TODO fill in JSON types
    ],
    name='interface-set'
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
    parameters=[
        Parameter('initial_states', compiler_for('volume'),
                  description="initial states for this transition"),
        Parameter('final_states', compiler_for('volume'),
                  description="final states for this transition")
    ],
    name='tps'
)

build_tps_network = TPS_NETWORK_PLUGIN

MISTIS_NETWORK_PLUGIN = NetworkCompilerPlugin(
    parameters=[Parameter('trans_info', mistis_trans_info)],
    builder=Builder('openpathsampling.MISTISNetwork'),
    name='mistis'
)
build_mistis_network = MISTIS_NETWORK_PLUGIN

TIS_NETWORK_PLUGIN = NetworkCompilerPlugin(
    builder=Builder('openpathsampling.MISTISNetwork'),
    parameters=[Parameter('trans_info', tis_trans_info)],
    name='tis'
)
build_tis_network = TIS_NETWORK_PLUGIN


NETWORK_COMPILER = CompilerPlugin(NetworkCompilerPlugin, aliases=['networks'])

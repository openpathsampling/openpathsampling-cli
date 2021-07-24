from paths_cli.parsing.core import InstanceBuilder, Parser
from paths_cli.parsing.tools import custom_eval
from paths_cli.parsing.volumes import volume_parser
from paths_cli.parsing.cvs import cv_parser

build_interface_set = InstanceBuilder(
    module='openpathsampling',
    builder='VolumeInterfaceSet',
    attribute_table={
        'cv': cv_parser,
        'minvals': custom_eval,
        'maxvals': custom_eval,
    }
)

def mistis_trans_info(dct):
    dct = dct.copy()
    transitions = dct.pop('transitions')
    trans_info = [
        (
            volume_parser(trans['initial_state']),
            build_interface_set(trans['interfaces']),
            volume_parser(trans['final_state'])
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

build_tps_network = InstanceBuilder(
    module='openpathsampling',
    builder='TPSNetwork',
    attribute_table={
        'initial_states': volume_parser,
        'final_states': volume_parser,
    }
)

build_mistis_network = InstanceBuilder(
    module='openpathsampling',
    builder='MISTISNetwork',
    attribute_table={'trans_info': mistis_trans_info},
)

build_tis_network = InstanceBuilder(
    module='openpathsampling',
    builder='MISTISNetwork',
    attribute_table={'trans_info': tis_trans_info},
)

TYPE_MAPPING = {
    'tps': build_tps_network,
    'tis': build_tis_network,
    'mistis': build_mistis_network,
}

network_parser = Parser(TYPE_MAPPING, label="networks")

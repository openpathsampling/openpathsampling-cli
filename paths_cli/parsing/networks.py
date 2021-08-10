from paths_cli.parsing.core import (
    InstanceBuilder, Parser, Builder, Parameter
)
from paths_cli.parsing.tools import custom_eval
from paths_cli.parsing.volumes import volume_parser
from paths_cli.parsing.cvs import cv_parser

build_interface_set = InstanceBuilder(
    builder=Builder('openpathsampling.VolumeInterfaceSet'),
    parameters=[
        Parameter('cv', cv_parser, description="the collective variable "
                  "for this interface set"),
        Parameter('minvals', custom_eval), # TODO fill in JSON types
        Parameter('maxvals', custom_eval), # TODO fill in JSON types
    ],
    name='volume-interface-set'
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
    builder=Builder('openpathsampling.TPSNetwork'),
    parameters=[
        Parameter('initial_states', volume_parser,
                  description="initial states for this transition"),
        Parameter('final_states', volume_parser,
                  description="final states for this transition")
    ],
    name='tps'
)

build_mistis_network = InstanceBuilder(
    parameters=[Parameter('trans_info', mistis_trans_info)],
    builder=Builder('openpathsampling.MISTISNetwork'),
    name='mistis'
)

build_tis_network = InstanceBuilder(
    builder=Builder('openpathsampling.MISTISNetwork'),
    parameters=[Parameter('trans_info', tis_trans_info)],
    name='tis'
)

TYPE_MAPPING = {
    'tps': build_tps_network,
    'tis': build_tis_network,
    'mistis': build_mistis_network,
}

network_parser = Parser(TYPE_MAPPING, label="networks")

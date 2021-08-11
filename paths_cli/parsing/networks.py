from paths_cli.parsing.core import (
    InstanceBuilder, Parser, Builder, Parameter
)
from paths_cli.parsing.tools import custom_eval
from paths_cli.parsing.plugins import NetworkParserPlugin, ParserPlugin
from paths_cli.parsing.root_parser import parser_for

build_interface_set = InstanceBuilder(
    builder=Builder('openpathsampling.VolumeInterfaceSet'),
    parameters=[
        Parameter('cv', parser_for('cv'), description="the collective "
                  "variable for this interface set"),
        Parameter('minvals', custom_eval), # TODO fill in JSON types
        Parameter('maxvals', custom_eval), # TODO fill in JSON types
    ],
    name='interface-set'
)

def mistis_trans_info(dct):
    dct = dct.copy()
    transitions = dct.pop('transitions')
    volume_parser = parser_for('volume')
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

build_tps_network = NetworkParserPlugin(
    builder=Builder('openpathsampling.TPSNetwork'),
    parameters=[
        Parameter('initial_states', parser_for('volume'),
                  description="initial states for this transition"),
        Parameter('final_states', parser_for('volume'),
                  description="final states for this transition")
    ],
    name='tps'
)

build_mistis_network = NetworkParserPlugin(
    parameters=[Parameter('trans_info', mistis_trans_info)],
    builder=Builder('openpathsampling.MISTISNetwork'),
    name='mistis'
)

build_tis_network = NetworkParserPlugin(
    builder=Builder('openpathsampling.MISTISNetwork'),
    parameters=[Parameter('trans_info', tis_trans_info)],
    name='tis'
)

NETWORK_PARSER = ParserPlugin(NetworkParserPlugin, aliases=['networks'])

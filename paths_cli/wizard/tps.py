from paths_cli.wizard.tools import a_an
from paths_cli.wizard.core import get_missing_object
from paths_cli.wizard.shooting import shooting
from functools import partial

def _get_network(wizard):
    if len(wizard.networks) == 0:
        network = tps_network(wizard)
    elif len(wizard.networks) == 1:
        network = list(wizard.networks.values())[0]
    else:
        networks = list(wizard.networks.keys())
        sel = wizard.ask_enumerate("Which network would you like to use?",
                                   options=networks)
        network = wizard.networks[sel]
    return network

def tps_scheme(wizard, network=None):
    import openpathsampling as paths
    from openpathsampling import strategies
    if network is None:
        network = get_missing_object(wizard, wizard.networks, 'network',
                                     tps_network)

    shooting_strategy = shooting(wizard)
    # TODO: add an option for shifting maybe?
    global_strategy = strategies.OrganizeByMoveGroupStrategy()
    scheme = paths.MoveScheme(network)
    scheme.append(shooting_strategy)
    scheme.append(global_strategy)
    return scheme

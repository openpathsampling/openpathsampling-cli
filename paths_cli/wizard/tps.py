from paths_cli.wizard.tools import a_an
from paths_cli.wizard.core import get_missing_object
from paths_cli.wizard.shooting import shooting
from functools import partial


def tps_scheme(wizard, network=None):
    import openpathsampling as paths
    from openpathsampling import strategies
    if network is None:
        network = get_missing_object(wizard, wizard.networks, 'network',
                                     tps_network)

    shooting_strategy = shooting(wizard, network=network)

    if not isinstance(shooting_strategy, paths.MoveStrategy):
        # this means we got a fixed scheme and can't do strategies
        return shooting_strategy(network=network)

    # TODO: add an option for shifting maybe?
    global_strategy = strategies.OrganizeByMoveGroupStrategy()
    scheme = paths.MoveScheme(network)
    scheme.append(shooting_strategy)
    scheme.append(global_strategy)
    return scheme

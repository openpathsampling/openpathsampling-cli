from paths_cli.wizard.core import get_missing_object
from paths_cli.wizard.shooting import shooting
from paths_cli.wizard.plugin_registration import get_category_wizard

volumes = get_category_wizard('volume')


def tps_network(wizard):
    raise NotImplementedError("Still need to add other network choices")


def tps_scheme(wizard, network=None):
    import openpathsampling as paths
    from openpathsampling import strategies
    if network is None:
        network = get_missing_object(wizard, wizard.networks, 'network',
                                     tps_network)

    shooting_strategy = shooting(wizard)

    if not isinstance(shooting_strategy, strategies.MoveStrategy):
        # this means we got a fixed scheme and can't do strategies
        return shooting_strategy(network=network)

    # TODO: add an option for shifting maybe?
    global_strategy = strategies.OrganizeByMoveGroupStrategy()
    scheme = paths.MoveScheme(network)
    scheme.append(shooting_strategy)
    scheme.append(global_strategy)
    return scheme

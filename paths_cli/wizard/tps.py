from paths_cli.wizard.tools import a_an
from paths_cli.wizard.core import get_missing_object
from paths_cli.wizard.shooting import (
    shooting,
    # ALGORITHMS
    one_way_shooting,
    two_way_shooting,
    spring_shooting,
    # SELECTORS
    uniform_selector,
    gaussian_selector,
    # MODIFIERS
    random_velocities,
    # all_atom_delta_v,
    # single_atom_delta_v,
)
from functools import partial

def _select_states(wizard, state_type):
    states = []
    do_another = True
    while do_another:
        options = [name for name in wizard.states
                   if name not in states]
        done = f"No more {state_type} states to select"
        if len(states) >= 1:
            options.append(done)

        state = wizard.ask_enumerate(
            f"Pick a state to use for as {a_an(state_type)} {state_type} "
            "state", options=options
        )
        if state == done:
            do_another = False
        else:
            states.append(state)

    state_objs = [wizard.states[state] for state in states]
    return state_objs

def _get_pathlength(wizard):
    pathlength = None
    while pathlength is None:
        len_str = wizard.ask("How long (in frames) do you want yout "
                             "trajectories to be?")
        try:
            pathlength = int(len_str)
        except Exceptions as e:
            wizard.exception(f"Sorry, I couldn't make '{len_str}' into "
                             "an integer.", e)
    return pathlength

def flex_length_tps_network(wizard):
    import openpathsampling as paths
    initial_states = _select_states(wizard, 'initial')
    final_states = _select_states(wizard, 'final')
    network = paths.TPSNetwork(initial_states, final_states)
    return network

def fixed_length_tps_network(wizard):
    pathlength = _get_pathlength(wizard)
    initial_states = _select_states(wizard, 'initial')
    final_states = _select_states(wizard, 'final')
    network = paths.FixedLengthTPSNetwork(initial_states, final_states,
                                          length=pathlength)
    return network

def tps_network(wizard):
    import openpathsampling as paths
    FIXED = "Fixed length TPS"
    FLEX = "Flexible length TPS"
    tps_types = {
        FLEX: paths.TPSNetwork,
        FIXED: paths.FixedLengthTPSNetwork,
    }
    network_type = None
    while network_type is None:
        network_type = wizard.ask_enumerate(
            "Do you want to do flexible path length TPS (recommended) "
            "or fixed path length TPS?", options=list(tps_types.keys())
        )
        network_class = tps_types[network_type]

    if network_type == FIXED:
        pathlength = _get_pathlength(wizard)
        network_class = partial(network_class, length=pathlength)

    initial_states = _select_states(wizard, 'initial')
    final_states = _select_states(wizard, 'final')

    # TODO: summary

    obj = network_class(initial_states, final_states)
    return obj

def _get_network(wizard):
    if len(wizard.networks) == 0:
        network = tps_network(wizard)
    elif len(wizard.networks) == 1:
        network = list(wizard.networks.values())[0]
    else:
        networks = list(wizard.networks.keys())
        sel = wizard.ask_enumerate("Which network would you like to use?",
                                   options=networks)
        network = wizard.networks[network]
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

def tps_finalize(wizard):
    pass

def tps_setup(wizard):
    network = tps_network(wizard)
    scheme = tps_scheme(wizard, network)
    # name it
    # provide final info on how to use it
    return scheme


if __name__ == "__main__":
    from paths_cli.wizard.wizard import Wizard
    wiz = Wizard({'tps_network': ('networks', 1, '='),
                  'tps_scheme': ('schemes', 1, '='),
                  'tps_finalize': (None, None, None)})

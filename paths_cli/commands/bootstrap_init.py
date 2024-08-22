import click
from paths_cli import OPSCommandPlugin
from paths_cli.parameters import (
    INIT_SNAP, MULTI_NETWORK, OUTPUT_FILE, INPUT_FILE, ENGINE
)
from paths_cli.param_core import OPSStorageLoadSingle, Option

INIT_STATE = OPSStorageLoadSingle(
    param=Option("--initial-state", help="initial state"),
    store='volumes'
)
FINAL_STATE = OPSStorageLoadSingle(
    param=Option("--final-state", help="final state"),
    store='volumes'
)

@click.command(
    "bootstrap-init",
    short_help="TIS interface set initial trajectories from a snapshot",
)
@INIT_STATE.clicked(required=True)
@FINAL_STATE.clicked(required=True)
@INIT_SNAP.clicked()
@MULTI_NETWORK.clicked()
@ENGINE.clicked()
@OUTPUT_FILE.clicked()
@INPUT_FILE.clicked()
def bootstrap_init(init_state, final_state, network, engine, init_snap,
                   output_file, input_file):
    """Use ``FullBootstrapping`` to create initial conditions for TIS.

    This approach starts from a snapshot, runs MD to generate an initial
    path for the innermost ensemble, and then performs one-way shooting
    moves within each ensemble until the next ensemble as reached. This
    continues until all ensembles have valid trajectories.

    Note that intermediate sampling in this is not saved to disk.
    """
    storage = INPUT_FILE.get(input_file)
    network = MULTI_NETWORK.get(storage, network)
    init_state = INIT_STATE.get(storage, init_state)
    final_state = FINAL_STATE.get(storage, final_stage)
    transition = network.transitions[(init_state, final_state)]
    bootstrap_init_main(
        init_frame=INIT_SNAP.get(storage, init_snap),
        network=network,
        engine=engine,
        transition=transition,
        output_storage=OUTPUT_FILE.get(output_file)
    )


def bootstrap_init_main(init_frame, network, engine, transition,
                        output_storage):
    all_states = set(network.initial_states) | set(network.final_states)
    allowed_states = {transition.initial_state, transition.final_state}
    forbidden_states = list(all_states - allowed_states)
    try:
        extra_ensembles = network.ms_outers
    except KeyError:
        extra_ensembles = None

    bootstrapper = paths.FullBootstrapping(
        transition=transition,
        snaphot=init_frame,
        engine=engine,
        forbidden_states=forbidden_states,
        extra_ensembles=extra_ensembles,
    )
    init_conds = bootstrapper.run()
    if output_storage:
        output_storage.tags['final_conditions'] = init_conds

    return init_conds, bootstrapper


PLUGIN = OPSCommandPlugin(
    command=bootstrap_init,
    section="Simulation",
    requires_ops=(1, 0),
    requires_cli=(0, 4),
)

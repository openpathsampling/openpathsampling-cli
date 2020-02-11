import click
from paths_cli.parameters import (
    INPUT_FILE, OUTPUT_FILE, ENGINE, STATES, INIT_CONDS, N_STEPS_MC
)

import openpathsampling as paths

@click.command(
    "tps",
    short_help="Run transition path sampling simulations",
)
@INPUT_FILE.clicked(required=True)
@OUTPUT_FILE.clicked(required=True)
@STATES.clicked(required=True)
@ENGINE.clicked(required=False)
@INIT_CONDS.clicked(required=False)
@N_STEPS_MC
def tps(input_file, engine, state, init_traj, output_file, nsteps):
    """Run transition path sampling using setup in INPUT_FILE."""
    storage = INPUT_FILE.get(input_file)
    tps_main(engine=ENGINE.get(storage, engine),
             states=[STATES.get(storage, s) for s in state],
             init_traj=INIT_CONDS.get(storage, init_traj),
             output_storage=OUTPUT_FILE.get(output_file),
             n_steps=nsteps)


def tps_main(engine, states, init_traj, output_storage, n_steps):
    network = paths.TPSNetwork(initial_states=states, final_states=states)
    scheme = paths.OneWayShootingMoveScheme(network, engine=engine)
    initial_conditions = \
            scheme.initial_conditions_from_trajectories(init_traj)
    simulation = paths.PathSampling(
        storage=output_storage,
        move_scheme=scheme,
        sample_set=initial_conditions
    )
    simulation.run(n_steps)
    output_storage.tags['final_conditions'] = simulation.sample_set
    return simulation.sample_set, simulation


CLI = tps
SECTION = "Simulation"

if __name__ == "__main__":
    tps()

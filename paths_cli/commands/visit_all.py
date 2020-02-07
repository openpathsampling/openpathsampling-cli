import click

from paths_cli.parameters import (INPUT_FILE, OUTPUT_FILE, ENGINE, STATES,
                                  INIT_SNAP)

@click.command(
    "visit-all",
    short_help="Run MD to generate initial trajectories",
)
@INPUT_FILE.clicked(required=True)
@OUTPUT_FILE.clicked(required=True)
@STATES.clicked(required=True)
@ENGINE.clicked(required=False)
@INIT_SNAP.clicked(required=False)
def visit_all(input_file, output_file, state, engine, init_frame):
    """Run until initial trajectory for TPS/MSTPS/MSTIS achieved.

    This runs until all given states have been visited. That creates a long
    trajectory, subtrajectories of which will work for the initial
    trajectories in TPS, MSTPS, or MSTIS. Typically, you'll use a different
    engine from the TPS production engine (often high temperature).
    """
    storage = INPUT_FILE.get(input_file)
    visit_all_main(
        output_storage=OUTPUT_FILE.get(output_file),
        states=STATES.get(storage, state),
        engine=ENGINE.get(storage, engine),
        initial_frame=INIT_SNAP.get(storage, init_frame)
    )


def visit_all_main(output_storage, states, engine, initial_frame):
    import openpathsampling as paths
    timestep = getattr(engine, 'timestep', None)
    visit_all_ens = paths.VisitAllStatesEnsemble(states, timestep=timestep)
    trajectory = engine.generate(initial_frame, [visit_all_ens.can_append])
    if output_storage is not None:
        output_storage.save(trajectory)
        output_storage.tags['final_conditions'] = trajectory

    return trajectory, None  # no simulation object to return here


CLI = visit_all
SECTION = "Simulation"
REQUIRES_OPS = (1, 0)

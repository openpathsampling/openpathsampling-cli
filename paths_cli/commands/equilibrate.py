import click
# import openpathsampling as paths

from paths_cli.parameters import (
    INPUT_FILE, OUTPUT_FILE, INIT_CONDS, SCHEME
)

@click.command(
    "equilibrate",
    short_help="Run equilibration for path sampling",
)
@INPUT_FILE.clicked(required=True)
@OUTPUT_FILE.clicked(required=True)
@SCHEME.clicked(required=False)
@INIT_CONDS.clicked(required=False)
@click.option('--multiplier', type=int, default=1,
              help=("run number of steps equal to MULTIPLIER times the "
                    + "number of stepss to decorrelate"))
@click.option("--extra-steps", type=int, default=0,
              help="run EXTRA-STEPS additional steps")
def equilibrate(input_file, output_file, scheme, init_conds, multiplier,
                extra_steps):
    """Run path sampling equilibration, based on INPUT_FILE.

    This just runs the normal path sampling simulation, but the number of
    steps depends on how long it takes to create  a fully decorrelated
    sample set (no frames from the initial trajectories are still active).

    If N_DECORR is the number of steps to fully decorrelate, the total
    number of steps run is: N_DECORR * MULTIPLIER + EXTRA_STEPS
    """
    storage = INPUT_FILE.get(input_file)
    equilibrate_main(
        output_storage=OUTPUT_FILE.get(output_file),
        scheme=SCHEME.get(storage, scheme),
        init_conds=INIT_CONDS.get(storage, init_conds),
        multiplier=multiplier,
        extra_steps=extra_steps
    )


def equilibrate_main(output_storage, scheme, init_conds, multiplier,
                     extra_steps):
    import openpathsampling as paths
    init_conds = scheme.initial_conditions_from_trajectories(init_conds)
    simulation = paths.PathSampling(
        storage=output_storage,
        move_scheme=scheme,
        sample_set=init_conds
    )
    simulation.run_until_decorrelated()
    n_decorr = simulation.step
    simulation.run(n_decorr * (multiplier - 1) + extra_steps)
    if output_storage:
        output_storage.tags['final_conditions'] = simulation.sample_set
        output_storage.tags['equilibrated'] = simulation.sample_set
    return simulation.sample_set, simulation


CLI = equilibrate
SECTION = "Simulation"
REQUIRES_OPS = (1, 2)

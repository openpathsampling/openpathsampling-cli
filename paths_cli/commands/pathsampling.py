import click
# import openpathsampling as paths

from paths_cli import OPSCommandPlugin
from paths_cli.parameters import (
    INPUT_FILE, OUTPUT_FILE, INIT_CONDS, SCHEME, N_STEPS_MC,
    SIMULATION_CV_MODE,
)


@click.command(
    "pathsampling",
    short_help="Run any path sampling simulation, including TIS variants",
)
@INPUT_FILE.clicked(required=True)
@OUTPUT_FILE.clicked(required=True)
@SCHEME.clicked(required=False)
@INIT_CONDS.clicked(required=False)
@N_STEPS_MC
@SIMULATION_CV_MODE.clicked()
def pathsampling(input_file, output_file, scheme, init_conds, nsteps,
                 cv_mode):
    """General path sampling, using setup in INPUT_FILE"""
    storage = INPUT_FILE.get(input_file)
    SIMULATION_CV_MODE(storage, cv_mode)
    pathsampling_main(output_storage=OUTPUT_FILE.get(output_file),
                      scheme=SCHEME.get(storage, scheme),
                      init_conds=INIT_CONDS.get(storage, init_conds),
                      n_steps=nsteps)

def pathsampling_main(output_storage, scheme, init_conds, n_steps):
    import openpathsampling as paths
    init_conds = scheme.initial_conditions_from_trajectories(init_conds)
    simulation = paths.PathSampling(
        storage=output_storage,
        move_scheme=scheme,
        sample_set=init_conds
    )
    simulation.run(n_steps)
    if output_storage:
        output_storage.tags['final_conditions'] = simulation.sample_set
    return simulation.sample_set, simulation


PLUGIN = OPSCommandPlugin(
    command=pathsampling,
    section="Simulation",
    requires_ops=(1, 0),
    requires_cli=(0, 3)
)

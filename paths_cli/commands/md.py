import functools
import operator

import click

from paths_cli.parameters import (INPUT_FILE, OUTPUT_FILE, ENGINE,
                                  MULTI_ENSEMBLE, INIT_SNAP)

@click.command(
    "md",
    short_help=("Run MD for fixed time or until a given ensemble is "
                "satisfied"),
)
@INPUT_FILE.clicked(required=True)
@OUTPUT_FILE.clicked(required=True)
@ENGINE.clicked(required=False)
@MULTI_ENSEMBLE.clicked(required=False)
@click.option('-n', '--nsteps', type=int,
              help="number of MD steps to run")
@INIT_SNAP.clicked(required=False)
def md(input_file, output_file, engine, ensemble, nsteps, init_frame):
    """Run MD for for time of steps or until ensembles are satisfied.
    """
    storage = INPUT_FILE.get(input_file)
    md_main(
        output_storage=OUTPUT_FILE.get(output_file),
        engine=ENGINE.get(storage, engine),
        ensembles=MULTI_ENSEMBLE.get(storage, ensemble),
        nsteps=nsteps,
        initial_frame=INIT_SNAP.get(storage, init_frame)
    )


def md_main(output_storage, engine, ensembles, nsteps, initial_frame):
    import openpathsampling as paths
    if nsteps is not None and ensembles:
        raise RuntimeError("Options --ensemble and --nsteps cannot both be"
                           " used at once.")

    if nsteps is not None:
        ens = paths.LengthEnsemble(nsteps)
    else:
        ens = functools.reduce(operator.and_, ensembles)

    trajectory = engine.generate(initial_frame, running=ens.can_append)
    if output_storage is not None:
        output_storage.save(trajectory)
        output_storage.tags['final_conditions'] = trajectory

    return trajectory, None

CLI = md
SECTION = "Simulation"
REQUIRES_OPS = (1, 0)


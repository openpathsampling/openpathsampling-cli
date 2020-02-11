import click
from paths_cli.parameters import (INPUT_FILE, OUTPUT_FILE, ENGINE, STATES,
                                  N_STEPS_MC, INIT_SNAP)
from paths_cli.commands.visit_all import visit_all_main
from paths_cli.commands.equilibrate import equilibrate_main
from paths_cli.commands.pathsampling import path_sampling_main


@click.command("one-pot-tps",
               short_help="Start from a single frame and end with full TPS")
@INPUT_FILE.clicked(required=True)
@OUTPUT_FILE.clicked(required=True)
@STATES.clicked(required=True)
@ENGINE.clicked(required=False)
@click.option("--engine-hot", required=False,
              help="high temperature engine for initial trajectory")
@INIT_SNAP.clicked(required=False)
@N_STEPS_MC
def one_pot_tps(input_file, output_file, state, nsteps, engine, engine_hot,
                init_frame):
    storage = INPUT_FILE.get(input_file)
    engine = ENGINE.get(storage, engine)
    engine_hot = engine if engine_hot is None else ENGINE.get(storage,
                                                              engine_hot)
    one_pot_tps_main(output_storage=OUTPUT_FILE.get(output_file),
                     states=STATES.get(storage, state),
                     engine=engine,
                     engine_hot=engine_hot,
                     initial_frame=INIT_SNAP.get(storage, init_frame),
                     nsteps=nsteps)


def one_pot_tps_main(output_storage, states, engine, engine_hot,
                     initial_frame, nsteps):
    import openpathsampling as paths
    network = paths.TPSNetwork.from_states_all_to_all(states)
    scheme = paths.OneWayShootingMoveScheme(network=network,
                                            selector=paths.UniformSelector(),
                                            engine=engine)
    trajectory, _ = visit_all_main(None, states, engine_hot, initial_frame)
    equil_multiplier = 1
    equil_extra = 0
    equil_set, _ = equilibrate_main(None, scheme, trajectory,
                                    equil_multiplier, equil_extra)
    return path_sampling_main(output_storage, scheme, equil_set, nsteps)

CLI = one_pot_tps
SECTION = "Workflow"
REQUIRES_OPS = (1, 2)

import click

import paths_cli.utils
from paths_cli.parameters import APPEND_FILE, ENGINE, MULTI_TAG
from paths_cli import OPSCommandPlugin


@click.command(
    "load-trajectory",
    short_help="Load an external trajectory file",
)
@click.argument('traj_file')
@click.option(
    '--top',
    help=(
        "Topology information (typically PDB). Only for required "
        "formats."
    ),
    default=None,
)
@APPEND_FILE.clicked(required=True)
@MULTI_TAG.clicked()
def load_trajectory(traj_file, top, append, tag):
    """Load a trajectory from a file.

    This uses MDTraj under the hood, and can load any file format that
    MDTraj can. NB: This stores in a format based on OpenMM snapshots.
    Trajectories loaded this way will work with engines compatible with
    that input (e.g., GROMACS).
    """
    import mdtraj as md
    from openpathsampling.engines.openmm.tools import ops_load_trajectory
    traj = ops_load_trajectory(traj_file, top=top)
    storage = append.get()
    storage.save(traj)
    for tag_name in tag:
        storage.tags[tag_name] = traj


    # tests:
    # * check that we load PDB
    # * check that if we load PDB with top as well works
    # * check that we can load trr / xtc files (only with top)
    # * maybe check for error if top doesn't match traj file? (atom numbers)

PLUGIN = OPSCommandPlugin(
    command=load_trajectory,
    section="Miscellaneous",
    requires_ops=(1, 6),
    requires_cli=(0, 4),
)

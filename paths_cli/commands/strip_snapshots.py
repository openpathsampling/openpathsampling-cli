import click
from paths_cli.parameters import (
    INPUT_FILE, OUTPUT_FILE, CVS
)

from tqdm.auto import tqdm

@click.command(
    'strip-snapshots',
    short_help="Remove coordinates/velocities from an OPS storage"
)
@INPUT_FILE.clicked(required=True)
@OUTPUT_FILE.clicked(required=True)
@CVS.clicked(required=False)
@click.option('--blocksize', type=int, default=10,
              help="block size for precomputing CVs")
def strip_snapshots(input_file, output_file, cv, blocksize):
    """
    Remove snapshot information (coordinates, velocities) from INPUT_FILE.

    By giving the --cv option (once for each CV), you can select to only
    save certain CVs. If you do not give that option, all CVs will be saved.
    """
    input_storage = INPUT_FILE.get(input_file)
    return strip_snapshots_main(
        input_storage=input_storage,
        output_storage=OUTPUT_FILE.get(output_file),
        cvs=CVS.get(input_storage, cv),
        blocksize=blocksize
    )


def make_blocks(listlike, blocksize):
    n_objs = len(listlike)
    n_blocks = (n_objs // blocksize) + 1
    minval = lambda i: i * blocksize
    maxval = lambda i: min((i + 1) * blocksize, n_objs)
    blocks = [listlike[minval(i):maxval(i)] for i in range(n_blocks)]
    return blocks


def precompute_cvs(cvs, block):
    for cv in cvs:
        cv.enable_diskcache()
        _ = cv(block)


def rewrite_file(stage_names, stage_mapping):
    stages = tqdm(stage_names)
    for stage in stages:
        stages.set_description("%s" % stage)
        store_func, inputs = stage_mapping[stage]
        for obj in tqdm(inputs):
            store_func(obj)


def strip_snapshots_main(input_storage, output_storage, cvs, blocksize):
    if not cvs:
        cvs = list(input_storage.cvs)

    # save template
    output_storage.save(input_storage.snapshots[0])

    precompute_func = lambda inps: precompute_cvs(cvs, inps)
    snapshot_proxies = input_storage.snapshots.all().as_proxies()
    snapshot_blocks = make_blocks(snapshot_proxies, blocksize)
    stages = ['precompute', 'cvs', 'snapshots', 'trajectories', 'steps']
    stage_mapping = {
        'precompute': (precompute_func, snapshot_blocks),
        'cvs': (output_storage.cvs.save, input_storage.cvs),
        'snapshots': (output_storage.snapshots.mention,
                      snapshot_proxies),
        'trajectories': (output_storage.trajectories.mention,
                         input_storage.trajectories),
        'steps': (output_storage.steps.save, input_storage.steps),
    }
    return rewrite_file(stages, stage_mapping)
    # for stage in stages:
        # stages.set_description("%s" % stage)
        # if stage == 'precompute':
            # block_precompute_cvs(cvs, snapshot_proxies, blocksize)
        # else:
            # store_func, inputs = {
                # 'cvs': (output_storage.cvs.save, input_storage.cvs),
                # 'snapshots': (output_storage.snapshots.mention,
                              # snapshot_proxies),
                # 'trajectories': (output_storage.trajectories.mention,
                                 # input_storage.trajectories),
                # 'steps': (output_storage.steps.save, input_storage.steps)
            # }[stage]
            # for obj in tqdm(inputs):
                # store_func(obj)


CLI = strip_snapshots
SECTION = "Miscellaneous"
REQUIRES_OPS = (1, 0)

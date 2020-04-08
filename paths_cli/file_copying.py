"""Tools to facilitate copying files.

This is mainly aimed at cases where a file is being copied with some sort of
modification, or where CVs need to be disk-cached.
"""

import click
from tqdm.auto import tqdm
from paths_cli.param_core import (
    Option, Argument, StorageLoader, OPSStorageLoadNames
)
from paths_cli.parameters import HELP_MULTIPLE

INPUT_APPEND_FILE = StorageLoader(
    param=Argument('append_file',
                   type=click.Path(writable=True, readable=True)),
    mode='a'
)


class PrecomputeLoadNames(OPSStorageLoadNames):
    def get(self, storage, name):
        if len(name) == 0:
            return list(getattr(storage, self.store))
        elif len(name) == 1 and name[0] == '--':
            return []

        return super(PrecomputeLoadNames, self).get(storage, name)


PRECOMPUTE_CVS = PrecomputeLoadNames(
    param=Option('--cv', type=str, multiple=True,
                 help=('name of CV to precompute; if not specified all will'
                       + ' be used' + HELP_MULTIPLE
                       + ' (use `--cv --` to disable precomputing)')),
    store='cvs'
)


def make_blocks(listlike, blocksize):
    """Make blocks out of a listlike object.

    Parameters
    ----------
    listlike : Iterable
        must be an iterable that supports slicing
    blocksize : int
        number of objects per block


    Returns
    -------
    List[List[Any]] :
        the input iterable chunked into blocks
    """
    n_objs = len(listlike)
    partial_block = 1 if n_objs % blocksize else 0
    n_blocks = (n_objs // blocksize) + partial_block
    minval = lambda i: i * blocksize
    maxval = lambda i: min((i + 1) * blocksize, n_objs)
    blocks = [listlike[minval(i):maxval(i)] for i in range(n_blocks)]
    return blocks


def precompute_cvs(cvs, block):
    """Calculate a CV for a a given block.

    Parameters
    ----------
    cvs : List[:class:`openpathsampling.CollectiveVariable`]
        CVs to precompute
    block : List[Any]
        b
    """
    for cv in cvs:
        cv.enable_diskcache()
        _ = cv(block)


def precompute_cvs_func_and_inputs(input_storage, cvs, blocksize):
    """
    Parameters
    ----------
    input_storage : :class:`openpathsampling.Storage`
        storage file to read from
    cvs : List[:class:`openpathsampling.CollectiveVariable`]
        list of CVs to precompute; if None, use all CVs in ``input_storage``
    blocksize : int
        number of snapshots per block to precompute
    """
    if cvs is None:
        cvs = list(input_storage.cvs)

    precompute_func = lambda inps: precompute_cvs(cvs, inps)
    snapshot_proxies = input_storage.snapshots.all().as_proxies()
    snapshot_blocks = make_blocks(snapshot_proxies, blocksize)
    return precompute_func, snapshot_blocks


def rewrite_file(stage_names, stage_mapping):
    stages = tqdm(stage_names, desc="All stages")
    for stage in stages:
        store_func, inputs = stage_mapping[stage]
        desc = "This stage: {}".format(stage)
        for obj in tqdm(inputs, desc=desc, leave=False):
            store_func(obj)

import click
from paths_cli.param_core import (
    Option, Argument, OPSStorageLoadSingle, OPSStorageLoadMultiple,
    OPSStorageLoadNames, StorageLoader, GetByName, GetByNumber, GetOnly,
    GetOnlySnapshot, GetPredefinedName
)


HELP_MULTIPLE = "; may be used more than once"

ENGINE = OPSStorageLoadSingle(
    param=Option('-e', '--engine', help="identifer for the engine"),
    store='engines',
)

SCHEME = OPSStorageLoadSingle(
    param=Option('-m', '--scheme', help="identifier for the move scheme"),
    store='schemes',
)

class InitCondsLoader(OPSStorageLoadMultiple):
    def _extract_trajectories(self, obj):
        import openpathsampling as paths
        if isinstance(obj, paths.SampleSet):
            yield from (s.trajectory for s in obj)
        elif isinstance(obj, paths.Sample):
            yield obj.trajectory
        elif isinstance(obj, paths.Trajectory):
            yield obj
        elif isinstance(obj, list):
            for o in obj:
                yield from self._extract_trajectories(o)
        else:
            raise RuntimeError("Unknown initial conditions type: "
                               f"{obj} (type: {type(obj)}")

    def get(self, storage, names):
        results = super().get(storage, names)
        final_results = list(self._extract_trajectories(results))
        return final_results


INIT_CONDS = InitCondsLoader(
    param=Option('-t', '--init-conds', multiple=True,
                 help=("identifier for initial conditions "
                       + "(sample set or trajectory)" + HELP_MULTIPLE)),
    store='samplesets',
    value_strategies=[GetByName('tags'), GetByNumber('samplesets'),
                      GetByNumber('trajectories')],
    none_strategies=[GetOnly('samplesets'), GetOnly('trajectories'),
                     GetPredefinedName('tags', 'final_conditions'),
                     GetPredefinedName('tags', 'initial_conditions')]
)

INIT_SNAP = OPSStorageLoadSingle(
    param=Option('-f', '--init-frame',
                 help="identifier for initial snapshot"),
    store='snapshots',
    value_strategies=[GetByName('tags'), GetByNumber('snapshots')],
    none_strategies=[GetOnlySnapshot(),
                     GetPredefinedName('tags', 'initial_snapshot')]
)

CVS = OPSStorageLoadNames(
    param=Option('--cv', type=str, multiple=True,
                 help='name of CV' + HELP_MULTIPLE),
    store='cvs'
)

MULTI_VOLUME = OPSStorageLoadNames(
    param=Option('--volume', type=str, multiple=True,
                 help='name or index of volume' + HELP_MULTIPLE),
    store='volumes'
)

MULTI_ENGINE = OPSStorageLoadNames(
    param=Option('--engine', type=str, multiple=True,
                 help='name or index of engine' + HELP_MULTIPLE),
    store='engines'
)

MULTI_ENSEMBLE = OPSStorageLoadNames(
    param=Option('--ensemble', type=str, multiple=True,
                 help='name of index of ensemble' + HELP_MULTIPLE),
    store='ensembles'
)

STATES = OPSStorageLoadNames(
    param=Option('-s', '--state', type=str, multiple=True,
                 help='name  of state' + HELP_MULTIPLE),
    store='volumes'
)

MULTI_TAG = OPSStorageLoadNames(
    param=Option('--tag', type=str, multiple=True,
                 help='tag for object' + HELP_MULTIPLE),
    store='tags'
)

MULTI_NETWORK = OPSStorageLoadNames(
    param=Option('--network', type=str, multiple=True,
                 help='name or index of network' + HELP_MULTIPLE),
    store='networks'
)

MULTI_SCHEME = OPSStorageLoadNames(
    param=Option('--scheme', type=str, multiple=True,
                 help='name or index of move scheme' + HELP_MULTIPLE),
    store='schemes'
)

MULTI_INIT_SNAP = OPSStorageLoadMultiple(
    param=Option('-f', '--init-frame',
                 help="identifier for potential initial snapshots"),
    store='snapshots',
    value_strategies=[GetByName('tags'), GetByNumber('snapshots')],
    none_strategies=[GetOnlySnapshot(),
                     GetPredefinedName('tags', 'initial_snapshot')]
)

INPUT_FILE = StorageLoader(
    param=Argument('input_file',
                   type=click.Path(exists=True, readable=True)),
    mode='r'
)

OUTPUT_FILE = StorageLoader(
    param=Option('-o', '--output-file',
                 type=click.Path(writable=True),
                 help="output file"),
    mode='w'
)

APPEND_FILE = StorageLoader(
    param=Option('-a', '--append-file',
                 type=click.Path(writable=True, readable=True),
                 help="file to append to"),
    mode='a'
)

N_STEPS_MC = click.option('-n', '--nsteps', type=int,
                          help="number of Monte Carlo trials to run")

MULTI_CV = CVS

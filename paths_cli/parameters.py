import click
import os

_UNNAMED_STORES = ['snapshots', 'trajectories', 'samples', 'sample_sets',
                   'steps']


class AbstractParameter(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        if 'required' in kwargs:
            raise ValueError("Can't set required status now")
        self.kwargs = kwargs

    def clicked(self, required=False):
        raise NotImplementedError()

HELP_MULTIPLE = "; may be used more than once"

# we'll use tests of the -h option in the .travis.yml to ensure that the
# .clicked methods work
class Option(AbstractParameter):
    def clicked(self, required=False):  # no-cov
        return click.option(*self.args, **self.kwargs, required=required)

class Argument(AbstractParameter):
    def clicked(self, required=False):  # no-cov
        return click.argument(*self.args, **self.kwargs, required=required)


class AbstractLoader(object):
    def __init__(self, param):
        self.param = param

    @property
    def clicked(self):  # no-cov
        return self.param.clicked

    def get(self, *args, **kwargs):
        raise NotImplementedError()


class StorageLoader(AbstractLoader):
    def __init__(self, param, mode):
        super(StorageLoader, self).__init__(param)
        self.mode = mode

    def _workaround(self, name):
        # this is messed up... for some reason, storage doesn't create a new
        # file in append mode. That may be a bug
        import openpathsampling as paths
        if self.mode == 'a' and not os.path.exists(name):
            st = paths.Storage(name, mode='w')
            st.close()

    def get(self, name):
        import openpathsampling as paths
        self._workaround(name)
        return paths.Storage(name, mode=self.mode)


class OPSStorageLoadNames(AbstractLoader):
    """Simple loader that expects its input to be a name or index.
    """
    def __init__(self, param, store):
        super(OPSStorageLoadNames, self).__init__(param)
        self.store = store

    def get(self, storage, names):
        int_corrected = []
        for name in names:
            try:
                name = int(name)
            except ValueError:
                pass
            int_corrected.append(name)

        return [getattr(storage, self.store)[name]
                for name in int_corrected]


class Getter(object):
    def __init__(self, store_name):
        self.store_name = store_name

    def _get(self, storage, name):
        store = getattr(storage, self.store_name)
        try:
            return store[name]
        except:
            return None

class GetByName(Getter):
    def __call__(self, storage, name):
        return self._get(storage, name)

class GetByNumber(Getter):
    def __call__(self, storage, name):
        try:
            num = int(name)
        except:
            return None

        return self._get(storage, num)

class GetPredefinedName(Getter):
    def __init__(self, store_name, name):
        super().__init__(store_name=store_name)
        self.name = name

    def __call__(self, storage):
        return self._get(storage, self.name)

class GetOnly(Getter):
    def __call__(self, storage):
        store = getattr(storage, self.store_name)
        if len(store) == 1:
            return store[0]

class GetOnlyNamed(Getter):
    def __call__(self, storage):
        store = getattr(storage, self.store_name)
        named_things = [o for o in store if o.is_named]
        if len(named_things) == 1:
            return named_things[0]

class GetOnlySnapshot(Getter):
    def __init__(self, store_name="snapshots"):
        super().__init__(store_name)

    def __call__(self, storage):
        store = getattr(storage, self.store_name)
        if len(store) == 2:
            # this is really only 1 snapshot; reversed copy gets saved
            return store[0]


def _try_strategies(strategies, storage, **kwargs):
    result = None
    for strategy in strategies:
        result = strategy(storage, **kwargs)
        if result is not None:
            return result


class OPSStorageLoadSingle(AbstractLoader):
    """Objects that expect to load a single object.

    These can sometimes include guesswork to figure out which object is
    desired.
    """
    def __init__(self, param, store, value_strategies=None,
                 none_strategies=None):
        super(OPSStorageLoadSingle, self).__init__(param)
        self.store = store
        if value_strategies is None:
            value_strategies = [GetByName(self.store),
                                GetByNumber(self.store)]
        self.value_strategies = value_strategies

        if none_strategies is None:
            none_strategies = [GetOnly(self.store),
                               GetOnlyNamed(self.store)]
        self.none_strategies = none_strategies

    def get(self, storage, name):
        store = getattr(storage, self.store)
        # num_store = getattr(storage, self.num_store)

        if name is not None:
            result = _try_strategies(self.value_strategies, storage,
                                     name=name)
        else:
            result = _try_strategies(self.none_strategies, storage)

        if result is None:
            raise RuntimeError("Couldn't find %s", name)

        return result

ENGINE = OPSStorageLoadSingle(
    param=Option('-e', '--engine', help="identifer for the engine"),
    store='engines',
    # fallback=None  # for now... I'll add more tricks later
)

SCHEME = OPSStorageLoadSingle(
    param=Option('-m', '--scheme', help="identifier for the move scheme"),
    store='schemes',
    # fallback=None
)

INIT_CONDS = OPSStorageLoadSingle(
    param=Option('-t', '--init-conds',
                 help=("identifier for initial conditions "
                       + "(sample set or trajectory)")),
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

INPUT_FILE = StorageLoader(
    param=Argument('input_file',
                   type=click.Path(exists=True, readable=True)),
    mode='r'
)

OUTPUT_FILE = StorageLoader(
    param=Option('-o', '--output-file',
                 type=click.Path(writable=True),
                 help="output ncfile"),
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

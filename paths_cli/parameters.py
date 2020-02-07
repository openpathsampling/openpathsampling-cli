import click
import os
# import openpathsampling as paths

class AbstractParameter(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        if 'required' in kwargs:
            raise ValueError("Can't set required status now")
        self.kwargs = kwargs

    def clicked(self, required=False):
        raise NotImplementedError()

# we'll use tests of the -h option in the .travis.yml to ensure that the
# .clicked methods work

HELP_MULTIPLE = "; may be used more than once"

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


class OPSStorageLoadSingle(AbstractLoader):
    def __init__(self, param, store, fallback=None, num_store=None):
        super(OPSStorageLoadSingle, self).__init__(param)
        self.store = store
        self.fallback = fallback
        if num_store is None:
            num_store = store
        self.num_store = num_store

    def get(self, storage, name):
        store = getattr(storage, self.store)
        num_store = getattr(storage, self.num_store)

        result = None
        # if the we can get by name/number, do it
        if name is not None:
            try:
                result = store[name]
            except:
                # on any error, we try everything else
                pass

            if result is None:
                try:
                    num = int(name)
                except ValueError:
                    pass
                else:
                    result = num_store[num]

        if result is not None:
            return result

        # if only one is named, take it
        if self.store != 'tags' and name is None:
            # if there's only one of them, take that
            if len(store) == 1:
                return store[0]
            named_things = [o for o in store if o.is_named]
            if len(named_things) == 1:
                return named_things[0]

        if len(num_store) == 1 and name is None:
            return num_store[0]

        if self.fallback:
            result = self.fallback(self, storage, name)

        if result is None:
            raise RuntimeError("Couldn't find %s", name)

        return result


def init_traj_fallback(parameter, storage, name):
    result = None

    if isinstance(name, int):
        return storage.trajectories[name]

    if name is None:
        # fallback to final_conditions, initial_conditions, only trajectory
        # the "get" here may need to be changed for new storage
        for tag in ['final_conditions', 'initial_conditions']:
            result = storage.tags[tag]
            if result:
                return result

        # already tried storage.samplesets
        if len(storage.trajectories) == 1:
            return storage.trajectories[0]


def init_snap_fallback(parameter, storage, name):
    # this is structured so that other things can be added to it later
    result = None

    if name is None:
        result = storage.tags['initial_snapshot']
        if result:
            return result

        if len(storage.snapshots) == 2:
            # this is really only 1 snapshot; reversed copy gets saved
            return storage.snapshots[0]

ENGINE = OPSStorageLoadSingle(
    param=Option('-e', '--engine', help="identifer for the engine"),
    store='engines',
    fallback=None  # for now... I'll add more tricks later
)

SCHEME = OPSStorageLoadSingle(
    param=Option('-m', '--scheme', help="identifier for the move scheme"),
    store='schemes',
    fallback=None
)

INIT_CONDS = OPSStorageLoadSingle(
    param=Option('-t', '--init-conds',
                 help=("identifier for initial conditions "
                       + "(sample set or trajectory)")),
    store='tags',
    num_store='samplesets',
    fallback=init_traj_fallback
)

INIT_SNAP = OPSStorageLoadSingle(
    param=Option('-f', '--init-frame',
                 help="identifier for initial snapshot"),
    store='tags',
    num_store='snapshots',
    fallback=init_snap_fallback
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

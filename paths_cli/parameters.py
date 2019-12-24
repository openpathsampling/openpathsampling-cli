import click
import openpathsampling as paths

class AbstractParameter(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        if 'required' in kwargs:
            raise ValueError("Can't set required status now")
        self.kwargs = kwargs

    def clicked(self, required=False):
        raise NotImplementedError()

class Option(AbstractParameter):
    def clicked(self, required=False):
        return click.option(*self.args, **self.kwargs, required=required)

class Argument(AbstractParameter):
    def clicked(self, required=False):
        return click.argument(*self.args, **self.kwargs, required=required)


class AbstractLoader(object):
    def __init__(self, param):
        self.param = param

    @property
    def clicked(self):
        return self.param.clicked

    def get(self, *args, **kwargs):
        return NotImplementedError()


class StorageLoader(AbstractLoader):
    def __init__(self, param, mode):
        super(StorageLoader, self).__init__(param)
        self.mode = mode

    def get(self, name):
        return paths.Storage(name, mode=self.mode)


class OPSStorageLoadNames(AbstractLoader):
    def __init__(self, param, store):
        super(OPSStorageLoadNames, self).__init__(param)
        self.store = store

    def get(self, storage, name):
        return getattr(storage, self.store)[name]


class OPSStorageLoadSingle(OPSStorageLoadNames):
    def __init__(self, param, store, fallback=None, num_store=None):
        super(OPSStorageLoadSingle, self).__init__(param, store)
        self.fallback = fallback
        if num_store is None:
            num_store = store
        self.num_store = num_store

    def get(self, storage, name):
        store = getattr(storage, self.store)

        result = None
        # if the we can get by name/number, do it
        if name is not None:
            # note: new storage may do a try/except here
            result = store[name]

            if result is None:
                try:
                    num = int(name)
                except ValueError:
                    pass
                else:
                    num_store = getattr(storage, self.num_store)
                    result = num_store[num]

        if result is not None:
            return result

        # if there's only one of them, take that
        if len(store) == 1:
            return store[0]

        # if only one is named, take it
        named_things = [o for o in store if o.is_named]
        if len(named_things) == 1:
            return named_things[0]

        if self.fallback:
            result = self.fallback(self, storage, name)

        if result is None:
            raise RuntimeError("Couldn't find %s", name)

        return result

def init_traj_fallback(parameter, storage, name):
    result = None
    if name and os.path.isfile(name):
        # TODO: read from file
        pass

    if name is None:
        # fallback to final_conditions, initial_conditions, only trajectory
        # the "get" here may need to be changed for new storage
        for tag in ['final_conditions', 'initial_conditions']:
            result = storage.tags[tag]
            if result:
                return [result]

        if len(storage.samplesets) == 1:
            return [s.trajectory for s in storage.samplesets[0]]


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

INIT_TRAJ = OPSStorageLoadSingle(
    param=Option('-t', '--init-traj',
                 help="identifier for initial trajectory"),
    store='tags',
    num_store='trajectories',
    fallback=init_traj_fallback
)

CVS = OPSStorageLoadNames(
    param=Option('--cv', type=str, multiple=True,
                 help='name of CV; may select more than once'),
    store='cvs'
)

STATES = OPSStorageLoadNames(
    param=Option('-s', '--state', multiple=True,
                 help='name of state; may select more than once'),
    store='volumes'
)

INPUT_FILE = StorageLoader(
    param=Argument('input_file', type=str),
    mode='r'
)

OUTPUT_FILE = StorageLoader(
    param=Option('-o', '--output-file', type=str, help="output ncfile"),
    mode='w'
)

N_STEPS_MC = click.option('-n', '--nsteps', type=int,
                          help="number of Monte Carlo trials to run")

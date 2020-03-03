import click
import os


class AbstractParameter(object):
    """Abstract wrapper for click parameters.

    Forbids use setting ``required``, because we do that for each command
    individually.

    Parameters
    ----------
    args :
        args to pass to click parameters
    kwargs :
        kwargs to pass to click parameters
    """
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
    """Wrapper for click.option decorators"""
    def clicked(self, required=False):  # no-cov
        """Create the click decorator"""
        return click.option(*self.args, **self.kwargs, required=required)


class Argument(AbstractParameter):
    """Wrapper for click.argument decorators"""
    def clicked(self, required=False):  # no-cov
        """Create the click decorator"""
        return click.argument(*self.args, **self.kwargs, required=required)


class AbstractLoader(object):
    """Abstract object for getting relevant OPS object from the CLI.

    Parameters
    ----------
    param : :class:`.AbstractParameter`
        the Option or Argument wrapping a click decorator
    """
    def __init__(self, param):
        self.param = param

    @property
    def clicked(self):  # no-cov
        """Create the click decorator"""
        return self.param.clicked

    def get(self, *args, **kwargs):
        """Get the desired OPS object, based on the CLI input"""
        raise NotImplementedError()


class StorageLoader(AbstractLoader):
    """Open an OPS storage file

    Parameters
    ----------
    param : :class:`.AbstractParameter`
        the Option or Argument wrapping a click decorator
    mode : 'r', 'w', or 'a'
        the mode for the file
    """
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

    Parameters
    ----------
    param : :class:`.AbstractParameter`
        the Option or Argument wrapping a click decorator
    store : Str
        the name of the store to search
    """
    def __init__(self, param, store):
        super(OPSStorageLoadNames, self).__init__(param)
        self.store = store

    def get(self, storage, names):
        """Get the names from the storage

        Parameters
        ----------
        storage : :class:`openpathsampling.Storage`
            storage file to search in
        names : List[Str]
            names or numbers (as string) to use as keys to load from
            storage

        Returns
        -------
        List[Any] :
            the desired objects
        """
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
    """Abstract strategy for getting things from storage

    Parameters
    ----------
    store_name : Str
        the name of the storage to search
    """
    def __init__(self, store_name):
        self.store_name = store_name

    def _get(self, storage, name):
        store = getattr(storage, self.store_name)
        try:
            return store[name]
        except:
            return None


class GetByName(Getter):
    """Strategy using the CLI input as name for a stored item"""
    def __call__(self, storage, name):
        return self._get(storage, name)


class GetByNumber(Getter):
    """Strategy using the CLI input as numeric index of the stored item"""
    def __call__(self, storage, name):
        try:
            num = int(name)
        except:
            return None

        return self._get(storage, num)


class GetPredefinedName(Getter):
    """Strategy predefining name and store, allow default names"""
    def __init__(self, store_name, name):
        super().__init__(store_name=store_name)
        self.name = name

    def __call__(self, storage):
        return self._get(storage, self.name)


class GetOnly(Getter):
    """Strategy getting item from store if it is the only one"""
    def __call__(self, storage):
        store = getattr(storage, self.store_name)
        if len(store) == 1:
            return store[0]


class GetOnlyNamed(Getter):
    """Strategy selecting item from store if it is the only named item"""
    def __call__(self, storage):
        store = getattr(storage, self.store_name)
        named_things = [o for o in store if o.is_named]
        if len(named_things) == 1:
            return named_things[0]


class GetOnlySnapshot(Getter):
    """Strategy selecting only snapshot from a snapshot store"""
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
    desired. The details of how that guesswork is performed is determined
    by the strategy lists that are given.

    Parameters
    ----------
    param : :class:`.AbstractParameter`
        the Option or Argument wrapping a click decorator
    store : Str
        the name of the store to search
    value_strategies : List[Callable[(:class:`.Storage`, Str), Any]]
        The strategies to be used when the CLI provides a value for this
        parameter. Each should be a callable taking a storage and the string
        input from the CLI, and should return the desired object or None if
        it cannot be found.
    none_strategies : List[Callable[:class:`openpathsampling.Storage, Any]]
        The strategies to be used when the CLI does not provide a value for
        this parameter. Each should be a callable taking a storage, and
        returning the desired object or None if it cannot be found.
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
        """Load desired object from storage.

        Parameters
        ----------
        storage : openpathsampling.Storage
            the input storage to search
        name : Str or None
            string from CLI providing the identifier (name or index) for
            this object; None if not provided
        """
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

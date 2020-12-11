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
    has_simstore_patch = False
    def __init__(self, param, mode):
        super(StorageLoader, self).__init__(param)
        self.mode = mode

    @staticmethod
    def _is_simstore(name):
        return name.endswith(".db") or name.endswith(".sql")

    def _workaround(self, name):
        # this is messed up... for some reason, storage doesn't create a new
        # file in append mode. That may be a bug
        import openpathsampling as paths
        needs_workaround = (
            self.mode == 'a'
            and not os.path.exists(name)
            and not self._is_simstore(name)
        )
        if needs_workaround:
            st = paths.Storage(name, mode='w')
            st.close()

    def get(self, name):
        if self._is_simstore(name):
            import openpathsampling as paths
            from openpathsampling.experimental.storage import \
                    Storage, monkey_patch_all

            if not self.has_simstore_patch:
                paths = monkey_patch_all(paths)
                paths.InterfaceSet.simstore = True
                StorageLoader.has_simstore_patch = True

            from openpathsampling.experimental.simstore import \
                SQLStorageBackend
            backend = SQLStorageBackend(name, mode=self.mode)
            storage = Storage.from_backend(backend)
        else:
            from openpathsampling import Storage
            self._workaround(name)
            storage = Storage(name, self.mode)
        return storage


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

    def _min_num_snapshots(self, storage):
        # For netcdfplus, we see 2 snapshots when there is only one
        # (reversed copy gets saved). For SimStore, we see only one.
        import openpathsampling as paths
        if isinstance(storage, paths.netcdfplus.NetCDFPlus):
            min_snaps = 2
        else:
            min_snaps = 1
        return min_snaps

    def __call__(self, storage):
        store = getattr(storage, self.store_name)
        min_snaps = self._min_num_snapshots(storage)
        if len(store) == min_snaps:
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
            if name is None:
                msg = "Couldn't guess which item to use from " + self.store
            else:
                msg = "Couldn't find {name} is {store}".format(
                    name=name,
                    store=self.store
                )
            raise RuntimeError(msg)

        return result


class OPSStorageLoadMultiple(OPSStorageLoadSingle):
    """Objects that can guess a single object or have multiple specified.

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
    def get(self, storage, names):
        """Load desired objects from storage.

        Parameters
        ----------
        storage : openpathsampling.Storage
            the input storage to search
        names : List[Str] or None
            strings from CLI providing the identifier (name or index) for
            this object; None if not provided
        """
        if names == tuple():
            names = None

        if names is None or isinstance(names, (str, int)):
            listified = True
            names = [names]
        else:
            listified = False

        results = [super(OPSStorageLoadMultiple, self).get(storage, name)
                   for name in names]

        if listified:
            results = results[0]

        return results

import collections
import pkgutil
import importlib
import os

# TODO: this should be removed
OPSPlugin = collections.namedtuple(
    "OPSPlugin", ['name', 'location', 'func', 'section', 'plugin_type']
)

class PluginRegistrationError(RuntimeError):
    pass

# TODO: make more generic than OPS (requires_ops => requires_lib)
class Plugin(object):
    """Generic OPS plugin object"""
    def __init__(self, requires_ops, requires_cli):
        self.requires_ops = requires_ops
        self.requires_cli = requires_cli
        self.location = None
        self.plugin_type = None

    def attach_metadata(self, location, plugin_type):
        # error is already registered and data doesn't match
        error_condition = (
            (self.location is not None or self.plugin_type is not None)
            and (self.location != location
                 or self.plugin_type != plugin_type)
        )
        if error_condition:  # -no-cov-
            raise PluginRegistrationError(
                "The plugin " + repr(self) + "has been previously "
                "registered with different metadata."
            )
        self.location = location
        self.plugin_type = plugin_type


class OPSCommandPlugin(Plugin):
    """Plugin for subcommands to the OPS CLI"""
    def __init__(self, command, section, requires_ops=(1, 0),
                 requires_cli=(0, 4)):
        self.command = command
        self.section = section
        super().__init__(requires_ops, requires_cli)

    @property
    def name(self):
        return self.command.name

    @property
    def func(self):
        # TODO: this is temporary to minimally change the API
        # (this is what calling functions ask for
        return self.command

    def __repr__(self):
        return "OPSCommandPlugin(" + self.name + ")"

class CLIPluginLoader(object):
    """Abstract object for CLI plugins

    The overall approach involves 5 steps, each of which can be overridden:

    1. Find candidate plugins (which must be Python modules)
    2. Load the namespaces associated into a dict (nsdict)
    3. Based on those namespaces, validate that the module *is* a plugin
    4. Get the associated command name
    5. Return an OPSPlugin object for each plugin

    Details on steps 1, 2, and 4 differ based on whether this is a
    filesystem-based plugin or a namespace-based plugin.
    """
    def __init__(self, plugin_type, search_path, plugin_class=Plugin):
        self.plugin_type = plugin_type
        self.search_path = search_path
        self.plugin_class = plugin_class

    # TODO: this should be _find_candidate_modules
    def _find_candidates(self):
        raise NotImplementedError()

    @staticmethod
    def _make_nsdict(candidate):
        raise NotImplementedError()

    def _find_candidate_namespaces(self):
        candidates = self._find_candidates()
        namespaces = {cand: self._make_nsdict(cand) for cand in candidates}
        return namespaces

    def _is_my_plugin(self, obj):
        return isinstance(obj, self.plugin_class)

    def _find_plugins(self, namespaces):
        for loc, ns in namespaces.items():
            for obj in ns.values():
                if self._is_my_plugin(obj):
                    obj.attach_metadata(loc, self.plugin_type)
                    yield obj

    def __call__(self):
        namespaces = self._find_candidate_namespaces()
        plugins = list(self._find_plugins(namespaces))
        return plugins


class FilePluginLoader(CLIPluginLoader):
    """File-based plugins (quick and dirty)

    Parameters
    ----------
    search_path : str
        path to the directory that contains plugins (OS-dependent format)
    """
    def __init__(self, search_path, plugin_class):
        super().__init__(plugin_type="file", search_path=search_path,
                         plugin_class=plugin_class)

    def _find_candidates(self):
        def is_plugin(filename):
            return (
                filename.endswith(".py") and not filename.startswith("_")
                and not filename.startswith(".")
            )

        if not os.path.exists(os.path.join(self.search_path)):
            return []

        candidates = [os.path.join(self.search_path, f)
                      for f in os.listdir(self.search_path)
                      if is_plugin(f)]
        return candidates

    @staticmethod
    def _make_nsdict(candidate):
        ns = {}
        with open(candidate) as f:
            code = compile(f.read(), candidate, 'exec')
            eval(code, ns, ns)
        return ns


class NamespacePluginLoader(CLIPluginLoader):
    """Load namespace plugins (plugins for wide distribution)

    Parameters
    ----------
    search_path : str
        namespace (dot-separated) where plugins can be found
    """
    def __init__(self, search_path, plugin_class):
        super().__init__(plugin_type="namespace", search_path=search_path,
                         plugin_class=plugin_class)

    def _find_candidates(self):
        # based on https://packaging.python.org/guides/creating-and-discovering-plugins/#using-namespace-packages
        def iter_namespace(ns_pkg):
            return pkgutil.iter_modules(ns_pkg.__path__,
                                        ns_pkg.__name__ + ".")

        try:
            ns = importlib.import_module(self.search_path)
        except ModuleNotFoundError:
            candidates = []
        else:
            candidates = [
                importlib.import_module(name)
                for _, name, _ in iter_namespace(ns)
            ]
        return candidates

    @staticmethod
    def _make_nsdict(candidate):
        return vars(candidate)

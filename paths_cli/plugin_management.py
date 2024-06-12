import collections
import pkgutil
import importlib
import warnings
import os

class PluginRegistrationError(RuntimeError):
    pass

class Plugin(object):
    """Generic plugin object

    parameters
    ----------
    requires_lib: tuple
        tuple representing the minimum allowed version of the underlying
        library
    requires_cli: tuple
        tuple representing hte minimum allowed version of the command line
        interface application
    """
    def __init__(self, requires_lib, requires_cli):
        self.requires_lib = requires_lib
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
            msg = (
                f"The plugin {repr(self)} has been previously "
                "registered with different metadata."
            )
            raise PluginRegistrationError(msg)

        self.location = location
        self.plugin_type = plugin_type


class OPSPlugin(Plugin):
    """Generic OPS plugin object.

    Really just to rename ``requires_lib`` to ``requires_ops``.
    """
    def __init__(self, requires_ops, requires_cli):
        super().__init__(requires_ops, requires_cli)

    @property
    def requires_ops(self):
        return self.requires_lib


class OPSCommandPlugin(OPSPlugin):
    """Plugin for subcommands to the OPS CLI

    Parameters
    ----------
    command: :class:`click.Command`
        the ``click``-wrapped command for this command
    section: str
        the section of the help where this command should appear
    requires_ops: tuple
        the minimum allowed version of OPS
    requires_cli: tuple
        the minimum allowed version of the OPS CLI
    """
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
        return f"OPSCommandPlugin({self.name})"

class CLIPluginLoader(object):
    """Abstract object for CLI plugins

    The overall approach involves 3 steps:

    1. Find modules in the relevant locations
    2. Load the namespaces associated into a dict (nsdict)
    3. Find all objects in those namespaces that are plugins

    Additionally, we attach metadata about where the plugin was found and
    what mechamism it was loaded with.

    Details on steps 1 and 2 differ based on whether this is a
    filesystem-based plugin or a namespace-based plugin, and details on step
    3 can depend on the specific instance created. By default, it looks for
    instances of :class:`.Plugin` (given as ``plugin_class``) but the
    ``isinstance`` check can be overridden in subclasses.

    Parameters
    ----------
    plugin_type : Literal["file", "namespace"]
        the type of file
    search_path : str
        the directory or namespace to search for plugins
    plugin_class: type
        plugins are identified as instances of this class (override in
        ``_is_my_plugin``)
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
    plugin_class: type
        plugins are identified as instances of this class (override in
        ``_is_my_plugin``)
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
    plugin_class: type
        plugins are identified as instances of this class (override in
        ``_is_my_plugin``)
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

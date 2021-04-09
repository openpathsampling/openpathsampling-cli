import collections
import pkgutil
import importlib
import os

OPSPlugin = collections.namedtuple(
    "OPSPlugin", ['name', 'location', 'func', 'section', 'plugin_type']
)

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
    def __init__(self, plugin_type, search_path):
        self.plugin_type = plugin_type
        self.search_path = search_path

    def _find_candidates(self):
        raise NotImplementedError()

    @staticmethod
    def _make_nsdict(candidate):
        raise NotImplementedError()

    @staticmethod
    def _validate(nsdict):
        for attr in ['CLI', 'SECTION']:
            if attr not in nsdict:
                return False
        return True

    def _get_command_name(self, candidate):
        raise NotImplementedError()

    def _find_valid(self):
        candidates = self._find_candidates()
        namespaces = {cand: self._make_nsdict(cand) for cand in candidates}
        valid = {cand: ns for cand, ns in namespaces.items()
                 if self._validate(ns)}
        return valid

    def __call__(self):
        valid = self._find_valid()
        plugins = [
            OPSPlugin(name=self._get_command_name(cand),
                      location=cand,
                      func=ns['CLI'],
                      section=ns['SECTION'],
                      plugin_type=self.plugin_type)
            for cand, ns in valid.items()
        ]
        return plugins


class FilePluginLoader(CLIPluginLoader):
    """File-based plugins (quick and dirty)

    Parameters
    ----------
    search_path : str
        path to the directory that contains plugins (OS-dependent format)
    """
    def __init__(self, search_path):
        super().__init__(plugin_type="file", search_path=search_path)

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

    def _get_command_name(self, candidate):
        _, command_name = os.path.split(candidate)
        command_name = command_name[:-3]  # get rid of .py
        command_name = command_name.replace('_', '-')  # commands use -
        return command_name


class NamespacePluginLoader(CLIPluginLoader):
    """Load namespace plugins (plugins for wide distribution)

    Parameters
    ----------
    search_path : str
        namespace (dot-separated) where plugins can be found
    """
    def __init__(self, search_path):
        super().__init__(plugin_type="namespace", search_path=search_path)

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

    def _get_command_name(self, candidate):
        # +1 for the dot
        command_name = candidate.__name__
        command_name = command_name[len(self.search_path) + 1:]
        command_name = command_name.replace('_', '-')  # commands use -
        return command_name


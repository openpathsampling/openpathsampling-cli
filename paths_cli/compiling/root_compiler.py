from paths_cli.compiling.core import Compiler, InstanceBuilder
from paths_cli.compiling.plugins import CompilerPlugin

import logging
logger = logging.getLogger(__name__)

class CompilerRegistrationError(Exception):
    pass


# TODO: I think this is the only OPS-specific thing in here
_DEFAULT_COMPILE_ORDER = [
    'engine',
    'cv',
    'volume',
    'state',
    'network',
    'movescheme',
]

COMPILE_ORDER = _DEFAULT_COMPILE_ORDER.copy()

def clean_input_key(key):
    # TODO: move this to core
    """
    Canonical approach is to treat everything as lowercase with underscore
    separators. This will make everything lowercase, and convert
    whitespace/hyphens to underscores.
    """
    key = key.lower()
    key = "_".join(key.split())  # whitespace to underscore
    key.replace("-", "_")
    return key

### Managing known compilers and aliases to the known compilers ############

_COMPILERS = {}  # mapping: {canonical_name: Compiler}
_ALIASES = {}  # mapping: {alias: canonical_name}
# NOTE: _ALIASES does *not* include self-mapping of the canonical names

def _canonical_name(alias):
    """Take an alias or a compiler name and return the compiler name

    This also cleans user input (using the canonical form generated by
    :meth:`.clean_input_key`).
    """
    alias = clean_input_key(alias)
    alias_to_canonical = _ALIASES.copy()
    alias_to_canonical.update({pname: pname for pname in _COMPILERS})
    return alias_to_canonical.get(alias, None)

def _get_compiler(compiler_name):
    """
    _get_compiler must only be used after the compilers have been
    registered. It will automatically create a compiler for any unknown
    ``compiler_name.``
    """
    canonical_name = _canonical_name(compiler_name)
    # create a new compiler if none exists
    if canonical_name is None:
        canonical_name = compiler_name
        _COMPILERS[compiler_name] = Compiler(None, compiler_name)
    return _COMPILERS[canonical_name]

def _register_compiler_plugin(plugin):
    DUPLICATE_ERROR = RuntimeError(f"The name {plugin.name} has been "
                                   "reserved by another compiler")
    if plugin.name in _COMPILERS:
        raise DUPLICATE_ERROR

    compiler = _get_compiler(plugin.name)

    # register aliases
    new_aliases = set(plugin.aliases) - set([plugin.name])
    for alias in new_aliases:
        if alias in _COMPILERS or alias in _ALIASES:
            raise DUPLICATE_ERROR
        _ALIASES[alias] = plugin.name


### Handling delayed loading of compilers ##################################
#
# Many objects need to use compilers to create their input parameters. In
# order for them to be able to access dynamically-loaded plugins, we delay
# the loading of the compiler by using a proxy object.

class _CompilerProxy:
    def __init__(self, compiler_name):
        self.compiler_name = compiler_name

    @property
    def _proxy(self):
        canonical_name = _canonical_name(self.compiler_name)
        if canonical_name is None:
            raise RuntimeError("No compiler registered for "
                               f"'{self.compiler_name}'")
        return _get_compiler(canonical_name)

    @property
    def named_objs(self):
        return self._proxy.named_objs

    def __call__(self, *args, **kwargs):
        return self._proxy(*args, **kwargs)

def compiler_for(compiler_name):
    """Delayed compiler calling.

    Use this when you need to use a compiler as the loader for a  parameter.

    Parameters
    ----------
    compiler_name : str
        the name of the compiler to use
    """
    return _CompilerProxy(compiler_name)


### Registering builder plugins and user-facing register_plugins ###########

def _get_registration_names(plugin):
    """This is a trick to ensure that the names appear in the desired order.

    We always want the plugin name first, followed by aliases in order
    listed by the plugin creator. However, we only want each name to appear
    once.
    """
    ordered_names = []
    found_names = set([])
    aliases = [] if plugin.aliases is None else plugin.aliases
    for name in [plugin.name] + aliases:
        if name not in found_names:
            ordered_names.append(name)
            found_names.add(name)
    return ordered_names

def _register_builder_plugin(plugin):
    compiler = _get_compiler(plugin.compiler_name)
    for name in _get_registration_names(plugin):
        compiler.register_builder(plugin, name)

def register_plugins(plugins):
    builders = []
    compilers = []
    for plugin in plugins:
        if isinstance(plugin, InstanceBuilder):
            builders.append(plugin)
        elif isinstance(plugin, CompilerPlugin):
            compilers.append(plugin)

    for plugin in compilers:
        _register_compiler_plugin(plugin)

    for plugin in builders:
        _register_builder_plugin(plugin)

### Performing the compiling of user input #################################

def _sort_user_categories(user_categories):
    """Organize user input categories into compile order.

    "Cateogories" are the first-level keys in the user input file (e.g.,
    'engines', 'cvs', etc.) There must be one Compiler per category.
    """
    user_to_canonical = {user_key: _canonical_name(user_key)
                         for user_key in user_categories}
    sorted_keys = sorted(
        user_categories,
        key=lambda x: COMPILE_ORDER.index(user_to_canonical[x])
    )
    return sorted_keys

def do_compile(dct):
    """Main function for compiling user input to objects.
    """
    objs = []
    for category in _sort_user_categories(dct):
        # func = COMPILERS[category]
        func = _get_compiler(category)
        yaml_objs = dct.get(category, [])
        print(f"{yaml_objs}")
        new = [func(obj) for obj in yaml_objs]
        objs.extend(new)
    return objs
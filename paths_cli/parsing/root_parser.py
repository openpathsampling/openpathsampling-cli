from paths_cli.parsing.core import Parser, InstanceBuilder
from paths_cli.parsing.engines import engine_parser
from paths_cli.parsing.cvs import cv_parser
from paths_cli.parsing.volumes import volume_parser
from paths_cli.parsing.networks import network_parser
from paths_cli.parsing.schemes import scheme_parser
from paths_cli.parsing.plugins import ParserPlugin


TYPE_MAPPING = {
    'engines': engine_parser,
    'cvs': cv_parser,
    'volumes': volume_parser,
    'states': volume_parser,
    'networks': network_parser,
    'moveschemes': scheme_parser,
}

_DEFAULT_PARSE_ORDER = [
    'engine',
    'cv',
    'volume',
    'state',
    'network',
    'movescheme',
]

PARSE_ORDER = _DEFAULT_PARSE_ORDER.copy()

PARSERS = {}
ALIASES = {}

def parser_for(parser_name):
    """Delayed parser calling.

    Use this when you need to use a parser as the loader for a  parameter.

    Parameters
    ----------
    parser_name : str
        the name of the parser to use
    """
    def load_and_call_parser(*args, **kwargs):
        return PARSER[parser_name](*args, **kwargs)
    return load_and_call_parser

def _get_parser(parser_name):
    """
    _get_parser must only be used after the parsers have been registered
    """
    parser = PARSERS.get(parser_name, None)
    if parser is None:
        parser = Parser(None, parser_name)
        PARSERS[parser_name] = parser
    return parser

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

def register_plugins(plugins):
    builders = []
    parsers = []
    for plugin in plugins:
        if isinstance(plugin, InstanceBuilder):
            builders.append(plugin)
        elif isinstance(plugin, ParserPlugin):
            parsers.append(plugin)

    for plugin in parsers:
        _register_parser_plugin(plugin)

    for plugin in builders:
        _register_builder_plugin(plugin)

def _register_builder_plugin(plugin):
    parser = _get_parser(plugin.parser_name)
    for name in _get_registration_names(plugin):
        parser.register_builder(plugin, name)

def _register_parser_plugin(plugin):
    DUPLICATE_ERROR = RuntimeError(f"The name {plugin.name} has been "
                                   "reserved by another parser")
    if plugin.name in PARSERS:
        raise DUPLICATE_ERROR

    parser = _get_parser(plugin.name)

    # register aliases
    new_aliases = set(plugin.aliases) - set([plugin.name])
    for alias in new_aliases:
        if alias in PARSERS or alias in ALIASES:
            raise DUPLICATE_ERROR
        ALIASES[alias] = plugin.name

### old versions

def register_builder(parser_name, name, builder):
    parser = TYPE_MAPPING[parser_name]
    parser.register_builder(builder, name)

def parse(dct):
    objs = []
    for category, func in TYPE_MAPPING.items():
        yaml_objs = dct.get(category, [])
        new = [func(obj) for obj in yaml_objs]
        objs.extend(new)
    return objs

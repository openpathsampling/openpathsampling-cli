import click

from paths_cli.parsing.root_parser import parse, register_plugins
from paths_cli.parameters import OUTPUT_FILE
from paths_cli.errors import MissingIntegrationError
from paths_cli import OPSCommandPlugin
from paths_cli.parsing.plugins import ParserPlugin, InstanceBuilder
from paths_cli.plugin_management import (
    NamespacePluginLoader, FilePluginLoader
)
import importlib
from paths_cli.utils import app_dir_plugins

def import_module(module_name, format_type=None, install=None):
    try:
        mod = importlib.import_module(module_name)
    except ImportError:
        if format_type is None:
            format_type = module_name

        msg = "Unable to find a parser for f{format_type} on your system."
        if install is not None:
            msg += " Please install f{install} to use this format."

        raise MissingIntegrationError(msg)
    return mod

def load_yaml(f):
    yaml = import_module('yaml', format_type="YAML", install="PyYAML")
    return yaml.load(f.read(), Loader=yaml.FullLoader)

def load_json(f):
    json = import_module('json')  # this should never fail... std lib!
    return json.loads(f.read())

# This is why we can't use TOML:
# https://github.com/toml-lang/toml/issues/553#issuecomment-444814690
# Conflicts with rules preventing mixed types in arrays. This seems to have
# relaxed in TOML 1.0, but the toml package doesn't support the 1.0
# standard. We'll add toml in once the pacakge supports the standard.

EXTENSIONS = {
    'yaml': load_yaml,
    'yml': load_yaml,
    'json': load_json,
    'jsn': load_json,
    # 'toml': load_toml,
}

def select_loader(filename):
    ext = filename.split('.')[-1]
    try:
        return EXTENSIONS[ext]
    except KeyError:
        raise RuntimeError(f"Unknown file extension: {ext}")

def load_plugins():
    plugin_types = (InstanceBuilder, ParserPlugin)
    plugin_loaders = [
        NamespacePluginLoader('paths_cli.parsing', plugin_types),
        FilePluginLoader(app_dir_plugins(posix=False), plugin_types),
        FilePluginLoader(app_dir_plugins(posix=True), plugin_types),
        NamespacePluginLoader('paths_cli_plugins', plugin_types)
    ]
    plugins = sum([loader() for loader in plugin_loaders], [])
    return plugins

@click.command(
    'compile',
)
@click.argument('input_file')
@OUTPUT_FILE.clicked(required=True)
def compile_(input_file, output_file):
    loader = select_loader(input_file)
    with open(input_file, mode='r') as f:
        dct = loader(f)

    plugins = load_plugins()
    register_plugins(plugins)

    objs = parse(dct)
    print(objs)
    storage = OUTPUT_FILE.get(output_file)
    storage.save(objs)

PLUGIN = OPSCommandPlugin(
    command=compile_,
    section="Debug",
    requires_ops=(1, 0),
    requires_cli=(0, 3)
)

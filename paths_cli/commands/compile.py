import click

from paths_cli.compiling.root_compiler import do_compile, register_plugins
from paths_cli.parameters import OUTPUT_FILE
from paths_cli.errors import MissingIntegrationError
from paths_cli import OPSCommandPlugin
from paths_cli.compiling.plugins import (
    CategoryPlugin, InstanceCompilerPlugin
)
from paths_cli.plugin_management import NamespacePluginLoader
import importlib
from paths_cli.utils import get_installed_plugins
from paths_cli.commands.contents import report_all_tables

# this is just to handle a nicer error
def import_module(module_name, format_type=None, install=None):
    try:
        mod = importlib.import_module(module_name)
    except ImportError:
        if format_type is None:
            format_type = module_name

        msg = f"Unable to find a compiler for {format_type} on your system."
        if install is not None:
            msg += f" Please install {install} to use this format."

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
# standard. We'll add toml in once the package supports the standard.

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

def register_installed_plugins():
    plugin_types = (InstanceCompilerPlugin, CategoryPlugin)
    plugins = get_installed_plugins(
        default_loader=NamespacePluginLoader('paths_cli.compiling',
                                             plugin_types),
        plugin_types=plugin_types
    )
    register_plugins(plugins)


@click.command(
    'compile',
    short_help="compile a description of OPS objects into a database",
)
@click.argument('input_file')
@OUTPUT_FILE.clicked(required=True)
def compile_(input_file, output_file):
    """Compile JSON or YAML description of OPS objects into a database.

    INPUT_FILE is a JSON or YAML file that describes OPS simulation
    objects (e.g., MD engines, state volumes, etc.). The output will be an
    OPS database containing those objects, which can be used as the input to
    many other CLI subcommands.
    """
    loader = select_loader(input_file)
    with open(input_file, mode='r') as f:
        dct = loader(f)

    register_installed_plugins()

    objs = do_compile(dct)
    print(f"Saving {len(objs)} user-specified objects to {output_file}....")
    storage = OUTPUT_FILE.get(output_file)
    storage.save(objs)
    report_all_tables(storage)


PLUGIN = OPSCommandPlugin(
    command=compile_,
    section="Simulation Setup",
    requires_ops=(1, 0),
    requires_cli=(0, 3)
)

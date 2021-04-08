import click

from paths_cli.parsing.root_parser import parse
from paths_cli.parameters import OUTPUT_FILE

def import_module(module_name):
    try:
        mod = __import__(module_name)
    except ImportError:
        # TODO: better error handling
        raise
    return mod

def load_yaml(f):
    yaml = import_module('yaml')
    return yaml.load(f.read(), Loader=yaml.FullLoader)

def load_json(f):
    json = import_module('json')  # this should never fail... std lib!
    return json.loads(f.read())

def load_toml(f):
    toml = import_module('toml')
    return toml.loads(f.read())

EXTENSIONS = {
    'yaml': load_yaml,
    'yml': load_yaml,
    'json': load_json,
    'jsn': load_json,
    'toml': load_toml,
}

def select_loader(filename):
    ext = filename.split('.')[-1]
    try:
        return EXTENSIONS[ext]
    except KeyError:
        raise RuntimeError(f"Unknown file extension: {ext}")

@click.command(
    'compile',
)
@click.argument('input_file')
@OUTPUT_FILE.clicked(required=True)
def compile_(input_file, output_file):
    loader = select_loader(input_file)
    with open(input_file, mode='r') as f:
        dct = loader(f)

    objs = parse(dct)
    # print(objs)
    storage = OUTPUT_FILE.get(output_file)
    storage.save(objs)


CLI = compile_
SECTION = "Debug"

from paths_cli.parsing.core import Parser
from paths_cli.parsing.engines import engine_parser
from paths_cli.parsing.cvs import cv_parser
from paths_cli.parsing.volumes import volume_parser
from paths_cli.parsing.networks import network_parser
from paths_cli.parsing.schemes import scheme_parser


TYPE_MAPPING = {
    'engines': engine_parser,
    'cvs': cv_parser,
    'volumes': volume_parser,
    'states': volume_parser,
    'networks': network_parser,
    'moveschemes': scheme_parser,
}

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

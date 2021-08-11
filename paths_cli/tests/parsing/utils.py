from paths_cli.parsing.core import Parser

def mock_parser(parser_name, type_dispatch=None, named_objs=None):
    if type_dispatch is None:
        type_dispatch = {}
    parser = Parser(type_dispatch, parser_name)
    if named_objs is not None:
        parser.named_objs = named_objs
    return parser

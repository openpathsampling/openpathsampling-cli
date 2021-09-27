from paths_cli.compiling.core import CategoryCompiler

def mock_compiler(category, type_dispatch=None, named_objs=None):
    if type_dispatch is None:
        type_dispatch = {}
    compiler = CategoryCompiler(type_dispatch, category)
    if named_objs is not None:
        compiler.named_objs = named_objs
    return compiler

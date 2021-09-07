from paths_cli.compiling.core import Compiler

def mock_compiler(compiler_name, type_dispatch=None, named_objs=None):
    if type_dispatch is None:
        type_dispatch = {}
    compiler = Compiler(type_dispatch, compiler_name)
    if named_objs is not None:
        compiler.named_objs = named_objs
    return compiler

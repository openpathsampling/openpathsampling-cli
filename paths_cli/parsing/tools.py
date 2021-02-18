def custom_eval(obj, named_objs=None):
    string = str(obj)
    # TODO: check that the only attribute access comes from a whitelist
    namespace = {
        'np': __import__('numpy'),
        'math': __import__('math'),
    }
    return eval(string, namespace)


class UnknownAtomsError(RuntimeError):
    pass

def mdtraj_parse_atomlist(inp_str, topology):
    # TODO: enable the parsing of either string-like atom labels or numeric
    try:
        arr = custom_eval(inp_str)
    except:
        pass  # on any error, we do it the hard way
    pass

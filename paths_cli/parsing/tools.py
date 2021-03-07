import numpy as np

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

def mdtraj_parse_atomlist(inp_str, n_atoms, topology=None):
    """
    n_atoms: int
        number of atoms expected
    """
    # TODO: change n_atoms to the shape desired?
    # TODO: enable the parsing of either string-like atom labels or numeric
    indices = custom_eval(inp_str)

    arr = np.array(indices)
    if arr.dtype != int:
        raise TypeError("Input is not integers")
    if arr.shape != (1, n_atoms):
        # try to clean it up
        if len(arr.shape) == 1 and arr.shape[0] ==  n_atoms:
            arr.shape = (1, n_atoms)
        else:
            raise TypeError(f"Invalid input. Requires {n_atoms} "
                            "atoms.")

    return arr

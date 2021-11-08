import numpy as np
from paths_cli.compiling.errors import InputError


def custom_eval(obj, named_objs=None):
    """Parse user input to allow simple math.

    This allows certain user input to be treated as a simplified subset of
    Python. In particular, this is intended to allow simple arithmetic. It
    allows use of the modules numpy (as ``np``) and math, which provide
    potentially useful functions (e.g., ``cos``) as well as constants (e.g.,
    ``pi``).
    """
    string = str(obj)
    # TODO: check that the only attribute access comes from a whitelist
    # (parse the AST for that)
    namespace = {
        'np': __import__('numpy'),
        'math': __import__('math'),
    }
    return eval(string, namespace)


def custom_eval_int(obj, named_objs=None):
    val = custom_eval(obj, named_objs)
    return int(val)


def custom_eval_int_strict_pos(obj, named_objs=None):
    val = custom_eval_int(obj, named_objs)
    if val <= 0:
        raise InputError(f"Positive integer required; found {val}")
    return val


def custom_eval_float(obj, named_objs=None):
    val = custom_eval(obj, named_objs)
    return float(val)


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
        if len(arr.shape) == 1 and arr.shape[0] == n_atoms:
            arr.shape = (1, n_atoms)
        else:
            raise TypeError(f"Invalid input. Requires {n_atoms} "
                            "atoms.")

    return arr

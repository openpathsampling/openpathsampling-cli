def interpret_req(req):
    """Create user-facing string representation of the input requirement.

    Parameters
    ----------
    req : Tuple[..., int, int]
        req[1] is the minimum number of objects to create; req[2] is the
        maximum number of objects to create

    Returns
    -------
    str :
        human-reading string for how many objects to create
    """
    _, min_, max_ = req
    string = ""
    if min_ == max_:
        return str(min_)

    if min_ >= 1:
        string += f"at least {min_}"

    if max_ < float("inf"):
        if string:
            string += " and "
        string += f"at most {max_}"

    return string


# TODO: REFACTOR: It looks like get_missing_object may be redundant with
# other code for obtaining prerequisites for a function
def get_missing_object(wizard, obj_dict, display_name, fallback_func):
    """Get a prerequisite object.

    The ``obj_dict`` here is typically a mapping of objects known by the
    Wizard. If it is empty, the ``fallback_func`` is used to create a new
    object. If it has exactly 1 entry, that is used implicitly. If it has
    more than 1 entry, the user must select which one to use.

    Parameters
    ----------
    wizard : :class:`.Wizard`
        the wizard for user interaction
    obj_dict : Dict[str, Any]
        mapping of object name to object
    display_name: str
        the user-facing name of this type of object
    fallback_func: Callable[:class:`.Wizard`] -> Any
        method to create a new object of this type

    Returns
    -------
    Any :
        the prerequisite object
    """
    if len(obj_dict) == 0:
        obj = fallback_func(wizard)
    elif len(obj_dict) == 1:
        obj = list(obj_dict.values())[0]
    else:
        objs = list(obj_dict.keys())
        sel = wizard.ask_enumerate(f"Which {display_name} would you like "
                                   "to use?", options=objs)
        obj = obj_dict[sel]
    return obj


def get_object(func):
    """Decorator to wrap methods for obtaining objects from user input.

    This decorator implements the user interaction loop when dealing with a
    single user input. The wrapped function is intended to create some
    object. If the user's input cannot create a valid object, the wrapped
    function should return None.

    Parameters
    ----------
    func : Callable
        object creation method to wrap; should return None on failure
    """
    # TODO: use functools.wraps?
    def inner(*args, **kwargs):
        obj = None
        while obj is None:
            obj = func(*args, **kwargs)
        return obj
    return inner

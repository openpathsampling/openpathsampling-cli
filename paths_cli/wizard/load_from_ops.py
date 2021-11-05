from paths_cli.parameters import INPUT_FILE
from paths_cli.wizard.core import get_object

from paths_cli.wizard.errors import FILE_LOADING_ERROR_MSG
LABEL = "Load existing from OPS file"


@get_object
def _get_ops_storage(wizard):
    filename = wizard.ask("What file can it be found in?",
                          default='filename')
    try:
        storage = INPUT_FILE.get(filename)
    except Exception as e:
        wizard.exception(FILE_LOADING_ERROR_MSG, e)
        return None

    return storage


@get_object
def _get_ops_object(wizard, storage, store_name, obj_name):
    store = getattr(storage, store_name)
    options = {obj.name: obj for obj in store if obj.is_named}
    result = wizard.ask_enumerate_dict(
        f"What's the name of the {obj_name} you want to load?",
        options
    )
    return result


def load_from_ops(wizard, store_name, obj_name):
    """Load an object from an OPS file

    Parameters
    ----------
    wizard : :class:`.Wizard`
        the wizard for user interaction
    store_name : str
        name of the store where this object will be found
    obj_name : str
        name of the object to load

    Returns
    -------
    Any :
        the object loaded from the file
    """
    # TODO: this might be replaced by something in compiling to load from
    # files
    wizard.say("Okay, we'll load it from an OPS file.")
    storage = _get_ops_storage(wizard)
    obj = _get_ops_object(wizard, storage, store_name, obj_name)
    return obj

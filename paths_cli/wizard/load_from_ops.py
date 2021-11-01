from paths_cli.parameters import INPUT_FILE
from paths_cli.wizard.core import get_object

from paths_cli.wizard.errors import FILE_LOADING_ERROR_MSG
LABEL = "Load existing from OPS file"


def named_objs_helper(storage, store_name):
    def list_items(user_input, context=None):
        store = getattr(storage, store_name)
        names = [obj for obj in store if obj.is_named]
        outstr = "\n".join(['* ' + obj.name for obj in names])
        return f"Here's what I found:\n\n{outstr}"

    return list_items


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
    wizard.say("Okay, we'll load it from an OPS file.")
    storage = _get_ops_storage(wizard)
    obj = _get_ops_object(wizard, storage, store_name, obj_name)
    return obj

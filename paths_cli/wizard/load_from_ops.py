LABEL = "Load existing from OPS file"
from paths_cli.parameters import INPUT_FILE

def named_objs_helper(storage, store_name):
    def list_items(wizard, user_input):
        store = getattr(storage, store_name)
        names = [obj for obj in store if obj.is_named]
        outstr = "\n".join(['* ' + obj.name for obj in names])
        wizard.say("Here's what I found:\n\n" + outstr)

    return list_items


def load_from_ops(wizard, store_name, obj_name):
    wizard.say("Okay, we'll load it from an OPS file.")
    storage = None
    while storage is None:
        filename = wizard.ask("What file can it be found in?",
                              default='filename')
        try:
            storage = INPUT_FILE.get(filename)
        except Exception as e:
            wizard.exception(FILE_LOADING_ERROR_MSG, e)
            # TODO: error handling

    obj = None
    while obj is None:
        name = wizard.ask(f"What's the name of the {obj_name} you want to "
                          "load? (Type '?' to get a list of them)",
                          helper=named_objs_helper(storage, store_name))
        if name:
            try:
                obj = getattr(storage, store_name)[name]
            except Exception as e:
                wizard.exception("Something went wrong when loading "
                                 f"{name}. Maybe check the spelling?", e)
    return obj

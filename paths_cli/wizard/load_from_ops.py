from paths_cli.parameters import INPUT_FILE
from paths_cli.wizard.core import get_object
from paths_cli.wizard.standard_categories import CATEGORIES

from paths_cli.wizard.errors import FILE_LOADING_ERROR_MSG
LABEL = "Load existing from OPS file"

def named_objs_helper(storage, store_name):
    def list_items(wizard, user_input):
        store = getattr(storage, store_name)
        names = [obj for obj in store if obj.is_named]
        outstr = "\n".join(['* ' + obj.name for obj in names])
        wizard.say(f"Here's what I found:\n\n{outstr}")

    return list_items

@get_object
def _get_ops_storage(wizard):
    filename = wizard.ask("What file can it be found in?",
                          default='filename')
    try:
        storage = INPUT_FILE.get(filename)
    except Exception as e:
        wizard.exception(FILE_LOADING_ERROR_MSG, e)
        return

    return storage

@get_object
def _get_ops_object(wizard, storage, store_name, obj_name):
    name = wizard.ask(f"What's the name of the {obj_name} you want to "
                      "load? (Type '?' to get a list of them)",
                      helper=named_objs_helper(storage, store_name))
    if name:
        try:
            obj = getattr(storage, store_name)[name]
        except Exception as e:
            wizard.exception("Something went wrong when loading "
                   f"{name}. Maybe check the spelling?", e)
            return
        else:
            return obj

def load_from_ops(wizard, store_name, obj_name):
    wizard.say("Okay, we'll load it from an OPS file.")
    storage = _get_ops_storage(wizard)
    obj = _get_ops_object(wizard, storage, store_name, obj_name)
    return obj


from paths_cli.plugin_management import OPSPlugin
class LoadFromOPS(OPSPlugin):
    def __init__(self, category, obj_name=None, store_name=None,
                 requires_ops=(1,0), requires_cli=(0,3)):
        super().__init__(requires_ops, requires_cli)
        self.category = category
        self.name = "Load existing from OPS file"
        if obj_name is None:
            obj_name = self._get_category_info(category).singular

        if store_name is None:
            store_name = self._get_category_info(category).storage
            
        self.obj_name = obj_name
        self.store_name = store_name

    @staticmethod
    def _get_category_info(category):
        try:
            return CATEGORIES[category]
        except KeyError:
            raise RuntimeError(f"No category {category}. Extra names must "
                               "be given explicitly")

    def __call__(self, wizard):
        wizard.say("Okay, we'll load it from an OPS file.")
        storage = _get_ops_storage(wizard)
        obj = _get_ops_storage(wizard, storage, self.store_name,
                               self.obj_name)

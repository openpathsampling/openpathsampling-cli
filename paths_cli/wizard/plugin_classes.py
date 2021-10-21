from paths_cli.plugin_management import OPSPlugin
from paths_cli.wizard.standard_categories import get_category_info
from paths_cli.wizard.load_from_ops import load_from_ops

class LoadFromOPS(OPSPlugin):
    def __init__(self, category, obj_name=None, store_name=None,
                 requires_ops=(1,0), requires_cli=(0,3)):
        super().__init__(requires_ops, requires_cli)
        self.category = category
        self.name = "Load existing from OPS file"
        if obj_name is None:
            obj_name = get_category_info(category).singular

        if store_name is None:
            store_name = get_category_info(category).storage

        self.obj_name = obj_name
        self.store_name = store_name

    def __call__(self, wizard):
        return load_from_ops(wizard, self.store_name, self.obj_name)

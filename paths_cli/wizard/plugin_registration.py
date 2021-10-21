from collections import defaultdict

from paths_cli.wizard.parameters import WizardObjectPlugin
from paths_cli.wizard.wrap_compilers import WrapCategory
from paths_cli.wizard.plugin_classes import LoadFromOPS
from paths_cli.utils import get_installed_plugins
from paths_cli.plugin_management import NamespacePluginLoader


class CategoryWizardPluginRegistrationError(Exception):
    pass

_CATEGORY_PLUGINS = {}

def get_category_wizard(category):
    def inner(wizard, context=None):
        try:
            plugin = _CATEGORY_PLUGINS[category]
        except KeyError:
            raise CategoryWizardPluginRegistrationError(
                f"No wizard plugin for '{category}'"
            )
        return plugin(wizard, context)
    return inner


def _register_category_plugin(plugin):
    if plugin.name in _CATEGORY_PLUGINS:
        raise CategoryWizardPluginRegistrationError(
            f"The category '{plugin.name}' has already been reserved "
            "by another wizard plugin."
        )
    _CATEGORY_PLUGINS[plugin.name] = plugin


def register_plugins(plugins):
    categories = []
    object_plugins = []
    for plugin in plugins:
        if isinstance(plugin, WrapCategory):
            categories.append(plugin)
        if isinstance(plugin, (WizardObjectPlugin, LoadFromOPS)):
            object_plugins.append(plugin)

    for plugin in categories:
        # print("Registering " + str(plugin))
        _register_category_plugin(plugin)

    for plugin in object_plugins:
        # print("Registering " + str(plugin))
        category = _CATEGORY_PLUGINS[plugin.category]
        # print(category)
        category.register_plugin(plugin)

def register_installed_plugins():
    plugin_types = (WrapCategory, WizardObjectPlugin)
    plugins = get_installed_plugins(
        default_loader=NamespacePluginLoader('paths_cli.wizard',
                                             plugin_types),
        plugin_types=plugin_types
    )
    register_plugins(plugins)

    file_loader_plugins = get_installed_plugins(
        default_loader=NamespacePluginLoader('paths_cli.wizard',
                                             LoadFromOPS),
        plugin_types=LoadFromOPS
    )
    register_plugins(file_loader_plugins)



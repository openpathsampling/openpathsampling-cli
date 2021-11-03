import logging
from paths_cli.wizard.plugin_classes import (
    LoadFromOPS, WizardObjectPlugin, WrapCategory
)
from paths_cli.utils import get_installed_plugins
from paths_cli.plugin_management import NamespacePluginLoader

logger = logging.getLogger(__name__)


class CategoryWizardPluginRegistrationError(Exception):
    """Error with wizard category plugin registration fails"""


_CATEGORY_PLUGINS = {}


def get_category_wizard(category):
    """Get the wizard category object of the given name.

    This is the user-facing way to load the wizard category plugins after
    they have been registered.

    Parameters
    ----------
    category : str
        name of the category to load

    Returns
    -------
    :class:`.WrapCategory` :
        wizard category plugin for the specified category
    """
    def inner(wizard, context=None):
        try:
            plugin = _CATEGORY_PLUGINS[category]
        except KeyError as exc:
            raise CategoryWizardPluginRegistrationError(
                f"No wizard plugin for '{category}'"
            ) from exc
        return plugin(wizard, context)
    return inner


def _register_category_plugin(plugin):
    """convenience to register plugin or error if already registered"""
    if plugin.name in _CATEGORY_PLUGINS:
        raise CategoryWizardPluginRegistrationError(
            f"The category '{plugin.name}' has already been reserved "
            "by another wizard plugin."
        )
    _CATEGORY_PLUGINS[plugin.name] = plugin


def register_plugins(plugins):
    """Register the given plugins for use with the wizard.

    Parameters
    ----------
    plugins : List[:class:`.OPSPlugin`]
        wizard plugins to register (including category plugins and object
        plugins)
    """
    categories = []
    object_plugins = []
    for plugin in plugins:
        if isinstance(plugin, WrapCategory):
            categories.append(plugin)
        if isinstance(plugin, (WizardObjectPlugin, LoadFromOPS)):
            object_plugins.append(plugin)

    for plugin in categories:
        logger.debug("Registering %s", str(plugin))
        _register_category_plugin(plugin)

    for plugin in object_plugins:
        category = _CATEGORY_PLUGINS[plugin.category]
        logger.debug("Registering %s", str(plugin))
        logger.debug("Category: %s", str(category))
        category.register_plugin(plugin)


def register_installed_plugins():
    """Register all Wizard plugins found in standard locations.

    This is a convenience to avoid repeating identification of wizard
    plugins. If something external needs to load all plugins (e.g., for
    testing or for a custom script), this is the method to use.
    """
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

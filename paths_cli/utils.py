import importlib
import pathlib
import click
from .plugin_management import FilePluginLoader, NamespacePluginLoader

def tag_final_result(result, storage, tag='final_conditions'):
    """Save results to a tag in storage.

    Parameters
    ----------
    result : UUIDObject
        the result to store
    storage : OPS storage
        the output storage
    tag : str
        the name to tag it with; default is 'final_conditions'
    """
    if storage:
        print("Saving results to output file....")
        storage.save(result)
        storage.tags[tag] = result


def import_thing(module, obj=None):
    result = importlib.import_module(module)
    if obj is not None:
        result = getattr(result, obj)
    return result


def app_dir_plugins(posix):  # covered as smoke tests (too OS dependent)
    return str(pathlib.Path(
        click.get_app_dir("OpenPathSampling", force_posix=posix)
    ).resolve() / 'cli-plugins')


def get_installed_plugins(default_loader, plugin_types):
    loaders = [default_loader] + [
        FilePluginLoader(app_dir_plugins(posix=False), plugin_types),
        FilePluginLoader(app_dir_plugins(posix=True), plugin_types),
        NamespacePluginLoader('paths_cli_plugins', plugin_types)

    ]
    plugins = set(sum([loader() for loader in loaders], []))
    return list(plugins)

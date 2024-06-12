import importlib
import pathlib
from collections import abc
import click
from .plugin_management import FilePluginLoader, NamespacePluginLoader


class OrderedSet(abc.MutableSet):
    """Set-like object with ordered iterator (insertion order).

    This is used to ensure that only one copy of each plugin is loaded
    (set-like behavior) while retaining the insertion order.

    Parameters
    ----------
    iterable : Iterable
        iterable of objects to initialize with
    """
    def __init__(self, iterable=None):
        self._set = set([])
        self._list = []
        if iterable is None:
            iterable = []
        for item in iterable:
            self.add(item)

    def __contains__(self, item):
        return item in self._set

    def __len__(self):
        return len(self._set)

    def __iter__(self):
        return iter(self._list)

    def add(self, item):
        if item in self._set:
            return
        self._set.add(item)
        self._list.append(item)

    def discard(self, item):
        self._list.remove(item)
        self._set.discard(item)


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
    plugins = OrderedSet(sum([loader() for loader in loaders], []))
    return list(plugins)

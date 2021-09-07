import importlib
import pathlib
import click

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


def app_dir_plugins(posix):
    return str(pathlib.Path(
        click.get_app_dir("OpenPathSampling", force_posix=posix)
    ).resolve() / 'cli-plugins')

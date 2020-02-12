import click
from paths_cli.parameters import (
    INPUT_FILE, APPEND_FILE, MULTI_CV, MULTI_ENGINE, MULTI_VOLUME,
    MULTI_NETWORK, MULTI_SCHEME, MULTI_TAG
)

@click.command(
    'append',
    short_help="add objects from INPUT_FILE  to another file"
)
@INPUT_FILE.clicked(required=True)
@APPEND_FILE.clicked(required=True)
@MULTI_ENGINE.clicked(required=False)
@MULTI_CV.clicked(required=False)
@MULTI_VOLUME.clicked(required=False)
@MULTI_NETWORK.clicked(required=False)
@MULTI_SCHEME.clicked(required=False)
@MULTI_TAG.clicked(required=False)
@click.option('--save-tag', type=str, default=None,
              help=("save object to a tag; requires that only one "
                    + "object be specfied. Can also be used to rename "
                    + "tagged objects. To append a tagged object without "
                    + "a tag, use --save-tag \"\""))
def append(input_file, append_file, engine, cv, volume, network, scheme,
           tag, save_tag):
    """Append objects from INPUT_FILE to another file.
    """
    storage = INPUT_FILE.get(input_file)
    output_storage = APPEND_FILE.get(append_file)
    params = [MULTI_ENGINE, MULTI_CV, MULTI_VOLUME, MULTI_NETWORK,
              MULTI_SCHEME, MULTI_TAG]
    args = [engine, cv, volume, network, scheme, tag]
    to_save = []
    for arg, param in zip(args, params):
        to_save.extend(param.get(storage, arg))

    to_save = [obj for obj in to_save if obj is not None]
    if save_tag is not None and len(to_save) != 1:
        raise RuntimeError("Can't identify the object to tag when saving "
                           + str(len(to_save)) + " objects.")

    for obj in to_save:
        output_storage.save(obj)

    if tag and len(tag) == 1 and save_tag is None:
        save_tag = tag[0]

    if save_tag:
        output_storage.tags[save_tag] = to_save[0]

    # TO TEST
    # 3. "untag" an object by not associating a tag in the new storage

    output_storage.close()
    storage.close()


CLI = append
SECTION = "Miscellaneous"
REQUIRES_OPS = (1, 0)

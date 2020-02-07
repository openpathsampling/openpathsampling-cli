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
def append(input_file, append_file, engine, cv, volume, network, scheme,
           tag):
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

    for obj in to_save:
        output_storage.save(obj)

    output_storage.close()


CLI = append
SECTION = "Miscellaneous"
REQUIRES_OPS = (1, 0)

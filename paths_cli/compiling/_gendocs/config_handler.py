from collections import namedtuple
from paths_cli.commands.compile import select_loader

DocCategoryInfo = namedtuple('DocCategoryInfo', ['header', 'description',
                                                 'type_required'],
                             defaults=[None, True])


def load_config(config_file):
    """Load a configuration file for gendocs.

    The configuration file should be YAML or JSON, and should map each
    category name to the headings necessary to fill a DocCategoryInfo
    instance.

    Parameters
    ----------
    config_file : str
        name of YAML or JSON file
    """
    loader = select_loader(config_file)
    with open(config_file, mode='r', encoding='utf-8') as f:
        dct = loader(f)

    result = {category: DocCategoryInfo(**details)
              for category, details in dct.items()}
    return result

from collections import namedtuple
from paths_cli.commands.compile import select_loader

DocCategoryInfo = namedtuple('DocCategoryInfo', ['header', 'description'],
                             defaults=[None])


def load_config(config_file):
    loader = select_loader(config_file)
    with open(config_file, mode='r') as f:
        dct = loader(f)

    result = {category: DocCategoryInfo(**details)
              for category, details in dct.items()}
    return result

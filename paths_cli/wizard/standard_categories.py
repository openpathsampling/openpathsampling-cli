from collections import namedtuple

Category = namedtuple('Category', ['name', 'singular', 'plural', 'storage'])

_CATEGORY_LIST = [
    Category(name='engine',
             singular='engine',
             plural='engines',
             storage='engines'),
    Category(name='cv',
             singular='CV',
             plural='CVs',
             storage='cvs'),
    Category(name='state',
             singular='state',
             plural='states',
             storage='volumes'),
    Category(name='volume',
             singular='volume',
             plural='volumes',
             storage='volumes'),
]

CATEGORIES = {cat.name: cat for cat in _CATEGORY_LIST}

def get_category_info(category):
    try:
        return CATEGORIES[category]
    except KeyError:
        raise RuntimeError(f"No category {category}. Names and store name "
                           "must be explicitly provided")

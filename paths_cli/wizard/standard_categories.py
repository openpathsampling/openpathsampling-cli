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
    """Obtain info for a stanard (or registered) category.

    This provides a convenience for mapping various string names, which is
    especially useful in user interactions. Each ``Category`` consists of:

    * ``name``: the name used by the plugin infrastructure
    * ``singular``: the singular name of the type as it should appear in
      user interaction
    * ``plural``: the plural name of the type as it should appear in user
      interactions
    * ``storage``: the (pseudo)store name in OPS; used for loading object of
      this category type by name.

    Parameters
    ----------
    category : str
        the name of the category to load
    """
    try:
        return CATEGORIES[category]
    except KeyError:
        raise RuntimeError(f"No category {category}. Names and store name "
                           "must be explicitly provided")

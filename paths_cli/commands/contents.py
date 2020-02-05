import click
from paths_cli.parameters import INPUT_FILE

@click.command(
    'contents',
    short_help="list named objects from an OPS .nc file",
)
@INPUT_FILE.clicked(required=True)
def contents(input_file):
    """List the names of named objects in an OPS .nc file.

    This is particularly useful when getting ready to use one of simulation
    scripts (i.e., to identify exactly how a state or engine is named.)
    """
    storage = INPUT_FILE.get(input_file)
    print(storage)
    store_section_mapping = {
        'CVs': storage.cvs, 'Volumes': storage.volumes,
        'Engines': storage.engines, 'Networks': storage.networks,
        'Move Schemes': storage.schemes,
        'Simulations': storage.pathsimulators,
    }
    for section, store in store_section_mapping.items():
        print(get_section_string_nameable(section, store,
                                          _get_named_namedobj))
    print(get_section_string_nameable('Tags', storage.tags, _get_named_tags))

    print("\nData Objects:")
    unnamed_sections = {
        'Steps': storage.steps, 'Move Changes': storage.movechanges,
        'SampleSets': storage.samplesets,
        'Trajectories': storage.trajectories, 'Snapshots': storage.snapshots
    }
    for section, store in unnamed_sections.items():
        print(get_unnamed_section_string(section, store))

def _item_or_items(count):
    return "item" if count == 1 else "items"

def get_unnamed_section_string(section, store):
    len_store = len(store)
    return (section + ": " + str(len_store) + " unnamed "
            + _item_or_items(len_store))

def _get_named_namedobj(store):
    return [item.name for item in store if item.is_named]

def _get_named_tags(store):
    return list(store.keys())

def get_section_string_nameable(section, store, get_named):
    out_str = ""
    len_store = len(store)
    out_str += (section + ": " + str(len_store) + " "
                + _item_or_items(len_store))
    named = get_named(store)
    n_unnamed = len_store - len(named)
    for name in named:
        out_str += "\n* " + name
    if n_unnamed > 0:
        prefix = "plus " if named else ""
        out_str += ("\n* " + prefix + str(n_unnamed) + " unnamed "
                    + _item_or_items(n_unnamed))
    return out_str

CLI = contents
SECTION = "Miscellaneous"
REQUIRES_OPS = (1, 0)

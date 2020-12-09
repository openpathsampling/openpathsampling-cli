import click
from paths_cli.parameters import INPUT_FILE

UNNAMED_SECTIONS = ['steps', 'movechanges', 'samplesets', 'trajectories',
                    'snapshots']

NAME_TO_ATTR = {
    'CVs': 'cvs',
    'Volumes': 'volumes',
    'Engines': 'engines',
    'Networks': 'networks',
    'Move Schemes': 'schemes',
    'Simulations': 'pathsimulators',
    'Tags': 'tags',
    'Steps': 'steps',
    'Move Changes': 'movechanges',
    'SampleSets': 'samplesets',
    'Trajectories': 'trajectories',
    'Snapshots': 'snapshots'
}

@click.command(
    'contents',
    short_help="list named objects from an OPS .nc file",
)
@INPUT_FILE.clicked(required=True)
@click.option('--table', type=str, required=False,
              help="table to show results from")
def contents(input_file, table):
    """List the names of named objects in an OPS .nc file.

    This is particularly useful when getting ready to use one of simulation
    scripts (i.e., to identify exactly how a state or engine is named.)
    """
    storage = INPUT_FILE.get(input_file)
    print(storage)
    if table is None:
        report_all_tables(storage)
    else:
        table_attr = table.lower()
        try:
            store = getattr(storage, table_attr)
        except AttributeError:
            raise click.UsageError("Unknown table: '" + table_attr + "'")
        else:
            print(get_section_string(table_attr, store))


def get_section_string(label, store):
    attr = NAME_TO_ATTR.get(label, label.lower())
    if attr in UNNAMED_SECTIONS:
        string = get_unnamed_section_string(label, store)
    elif attr in ['tag', 'tags']:
        string = get_section_string_nameable(label, store, _get_named_tags)
    else:
        string = get_section_string_nameable(label, store,
                                             _get_named_namedobj)
    return string


def report_all_tables(storage):
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
    data_object_mapping = {
        'Steps': lambda storage: storage.steps,
        'Move Changes': lambda storage: storage.movechanges,
        'SampleSets': lambda storage: storage.samplesets,
        'Trajectories': lambda storage: storage.trajectories,
        'Snapshots': lambda storage: storage.snapshots
    }

    for section, store_func in data_object_mapping.items():
        store = store_func(storage)
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

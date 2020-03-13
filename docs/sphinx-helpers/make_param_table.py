#!/usr/bin/env python

"""
This is a little tool to dynamically create the RST table for the list of
parameters. This tool should be run, and its results stored in the repo when
it needs to be updated. It is not run automatically as part of the docs
build process.
"""

import sys
import collections
import click

from paths_cli import parameters
from  paths_cli import param_core

TableEntry = collections.namedtuple("TableEntry",
                                    "param flags get_args help")

def is_click_decorator(thing):
    return getattr(thing, '__module__', None) == 'click.decorators'

def is_parameter(thing):
    return (isinstance(thing, param_core.AbstractLoader)
            or is_click_decorator(thing))

def rst_wrap(code):
    return "``" + code + "``"

def flags_help(click_decorator):
    closure = click_decorator.__closure__
    flags = ", ".join([rst_wrap(flag) for flag in closure[1].cell_contents])
    help_ = closure[0].cell_contents.get('help', '')
    return flags, help_

def get_args(parameter):
    if isinstance(parameter, param_core.StorageLoader):
        return "``name``"
    elif isinstance(parameter, (param_core.OPSStorageLoadNames,
                                param_core.OPSStorageLoadSingle)):
        return "``storage``, ``name``"
    elif is_click_decorator(parameter):
        return "No ``get`` function"
    else:
        return "Unknown"

def get_click_decorator(thing):
    if isinstance(thing, param_core.AbstractLoader):
        return thing.param.clicked()
    elif is_click_decorator(thing):
        return thing
    else:
        raise RuntimeError("Unable to get decorator")

def make_table_entry(name, param, decorator):
    flags, help_ = flags_help(decorator)
    args = get_args(param)
    return TableEntry(name, flags, args, help_)

def get_table_info():
    params = {name: getattr(parameters, name)
              for name in dir(parameters)
              if is_parameter(getattr(parameters, name))}
    click_decorator = {name: get_click_decorator(thing)
                       for name, thing in params.items()}
    table = [
        make_table_entry(rst_wrap(name), params[name], click_decorator[name])
        for name in params
    ]
    return table

def table_to_rst(table):
    out_str = [".. csv-table:: Built-In CLI Parameters"]
    out_str += [" "*3 + ':header: "Parameter", "Flags", "``get`` arguments"'
                + ', "Help"']
    out_str += [" "*3 + ':widths: 10, 15, 15, 60', ""]

    for row in table:
        quoted = ['"' + entry + '"' for entry in row]
        out_str += [" "*3 + ", ".join(quoted)]

    return "\n".join(out_str)

def main(output=None):
    if output is None:
        output = sys.stdout
    table_rows = get_table_info()
    output.write(table_to_rst(table_rows))


if __name__ == "__main__":
    main()

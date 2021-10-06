import paths_cli.wizard.openmm as openmm
from paths_cli.wizard.load_from_ops import (
    LoadFromOPS,
    load_from_ops, LABEL as load_label
)
from functools import partial

from paths_cli.wizard.wrap_compilers import WrapCategory

_ENGINE_HELP = "An engine describes how you'll do the actual dynamics."
ENGINE_PLUGIN = WrapCategory(
    name='engine',
    ask="What will you use for the underlying engine?",
    intro=("Let's make an engine. " + _ENGINE_HELP + " Most of the "
           "details are given in files that depend on the specific "
           "type of engine."),
    helper=_ENGINE_HELP
)

ENGINE_FROM_FILE = LoadFromOPS('engine')

# TEMPORARY
# from .openmm import OPENMM_PLUGIN
# plugins = [OPENMM_PLUGIN, ENGINE_FROM_FILE]
# for plugin in plugins:
#     ENGINE_PLUGIN.register_plugin(plugin)


if __name__ == "__main__":
    from paths_cli.wizard import wizard
    wiz = wizard.Wizard([])
    # TODO: normally will need to register plugins from this file first
    engine = ENGINE_PLUGIN(wiz)
    print(engine)


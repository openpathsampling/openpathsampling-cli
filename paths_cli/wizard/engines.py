import paths_cli.wizard.openmm as openmm
from paths_cli.wizard.load_from_ops import (
    load_from_ops, LABEL as load_label
)
from functools import partial

from paths_cli.wizard.wrap_compilers import WrapCategory

SUPPORTED_ENGINES = {}
for module in [openmm]:
    SUPPORTED_ENGINES.update(module.SUPPORTED)

SUPPORTED_ENGINES[load_label] = partial(load_from_ops,
                                        store_name='engines',
                                        obj_name='engine')

def engines(wizard):
    wizard.say("Let's make an engine. An engine describes how you'll do "
               "the actual dynamics. Most of the details are given "
               "in files that depend on the specific type of engine.")
    engine_names = list(SUPPORTED_ENGINES.keys())
    eng_name = wizard.ask_enumerate(
        "What will you use for the underlying engine?",
        options=engine_names
    )
    engine = SUPPORTED_ENGINES[eng_name](wizard)
    return engine

_ENGINE_HELP = "An engine describes how you'll do the actual dynamics."
ENGINE_PLUGIN = WrapCategory(
    name='engines',
    ask="What will you use for the underlying engine?",
    intro=("Let's make an engine. " + _ENGINE_HELP + " Most of the "
           "details are given in files that depend on the specific "
           "type of engine."),
    helper=_ENGINE_HELP
)


if __name__ == "__main__":
    from paths_cli.wizard import wizard
    wiz = wizard.Wizard([])
    choices = {
        "OpenMM": openmm.OPENMM_PLUGIN,
        load_label: partial(load_from_ops,
                            store_name='engines',
                            obj_name='engine')
    }
    ENGINE_PLUGIN.choices = choices
    engine = ENGINE_PLUGIN(wiz)
    print(engine)


import paths_cli.wizard.openmm as openmm
from load_from_ops import load_from_ops, LABEL as load_label
from functools import partial

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

if __name__ == "__main__":
    from paths_cli.wizard import wizard
    wiz = wizard.Wizard({'engines': ('engines', 1, '=')})
    wiz.run_wizard()


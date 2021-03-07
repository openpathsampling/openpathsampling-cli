from paths_cli.wizard.steps import (
    SINGLE_ENGINE_STEP, CVS_STEP, WizardStep
)
from paths_cli.wizard.volumes import volumes
from paths_cli.wizard.tps import tps_scheme
from paths_cli.wizard.wizard import Wizard

def two_state_tps(wizard, fixed_length=False):
    import openpathsampling as paths
    wizard.say("Now let's define the stable states for your system. "
               "Let's start with your initial state.")
    initial_state = volumes(wizard, as_state=True, intro="")
    wizard.register(initial_state, 'initial state', 'states')
    wizard.say("Next let's define your final state.")
    final_state = volumes(wizard, as_state=True, intro="")
    wizard.register(final_state, 'final state', 'states')
    if fixed_length:
        ...
    else:
        network = paths.TPSNetwork(initial_state, final_state)
    scheme = tps_scheme(wizard, network=network)
    return scheme


TWO_STATE_TPS_WIZARD = Wizard([
    SINGLE_ENGINE_STEP,
    CVS_STEP,
    WizardStep(func=two_state_tps,
               display_name="TPS setup",
               store_name='schemes',
               minimum=1,
               maximum=1)
])

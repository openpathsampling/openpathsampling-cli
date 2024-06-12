from paths_cli.wizard.plugin_registration import get_category_wizard
from paths_cli.wizard.tps import tps_scheme
from paths_cli.wizard.steps import (
    SINGLE_ENGINE_STEP, CVS_STEP, WizardStep
)
from paths_cli.wizard.wizard import Wizard
from paths_cli.wizard import pause
from paths_cli.wizard.volumes import _FIRST_STATE, _VOL_DESC

volumes = get_category_wizard('volume')


def two_state_tps(wizard, fixed_length=False):
    import openpathsampling as paths
    wizard.requirements['state'] = ('volumes', 2, 2)
    intro = [
        _FIRST_STATE.format(n_states_string=2),
        "Let's start with your initial state.",
        _VOL_DESC,
    ]
    initial_state = volumes(wizard, context={'intro': intro})
    wizard.register(initial_state, 'initial state', 'states')
    pause.section(wizard)
    intro = [
        "Next let's define your final state.",
        _VOL_DESC
    ]
    final_state = volumes(wizard, context={'intro': intro})
    wizard.register(final_state, 'final state', 'states')
    if fixed_length:
        ...  # no-cov  (will add this later)
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

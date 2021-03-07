from collections import namedtuple
from functools import partial

from paths_cli.wizard.cvs import cvs
from paths_cli.wizard.engines import engines
from paths_cli.wizard.volumes import volumes
from paths_cli.wizard.tps import (
    flex_length_tps_network, fixed_length_tps_network, tps_scheme
)

WizardStep = namedtuple('WizardStep', ['func', 'display_name', 'store_name',
                                       'minimum', 'maximum'])

SINGLE_ENGINE_STEP = WizardStep(func=engines,
                                display_name="engine",
                                store_name="engines",
                                minimum=1,
                                maximum=1)

CVS_STEP = WizardStep(func=cvs,
                      display_name="CV",
                      store_name='cvs',
                      minimum=1,
                      maximum=float('inf'))

MULTIPLE_STATES_STEP = WizardStep(func=partial(volumes, as_state=True),
                                  display_name="state",
                                  store_name="states",
                                  minimum=2,
                                  maximum=float('inf'))



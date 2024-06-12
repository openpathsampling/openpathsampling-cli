from collections import namedtuple
from paths_cli.wizard.plugin_registration import get_category_wizard

volumes = get_category_wizard('volume')

WizardStep = namedtuple('WizardStep', ['func', 'display_name', 'store_name',
                                       'minimum', 'maximum'])

SINGLE_ENGINE_STEP = WizardStep(func=get_category_wizard('engine'),
                                display_name="engine",
                                store_name="engines",
                                minimum=1,
                                maximum=1)

CVS_STEP = WizardStep(func=get_category_wizard('cv'),
                      display_name="CV",
                      store_name='cvs',
                      minimum=1,
                      maximum=float('inf'))

MULTIPLE_STATES_STEP = WizardStep(func=get_category_wizard('volume'),
                                  display_name="state",
                                  store_name="states",
                                  minimum=2,
                                  maximum=float('inf'))

from paths_cli.wizard.plugin_registration import register_installed_plugins
from paths_cli.wizard.wizard import Wizard
from paths_cli.wizard.plugin_registration import get_category_wizard

from paths_cli.wizard.parameters import WizardObjectPlugin
from paths_cli.wizard.load_from_ops import LoadFromOPS

# TODO: for now we ignore this for coverage -- it's mainly used for UX
# testing by allowing each module to be run with, e.g.:
#    python -m paths_cli.wizard.engines
# If that functionality is retained, it might be good to find a way to test
# this.
def run_category(category, requirements=None):  # -no-cov-
    # TODO: if we keep this, fix it up so that it also saves the resulting
    # objects
    register_installed_plugins()
    if requirements is None:
        requirements = {}
    wiz = Wizard({})
    wiz.requirements = requirements
    category_plugin = get_category_wizard(category)
    obj = category_plugin(wiz)
    print(obj)

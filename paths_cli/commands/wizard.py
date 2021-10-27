import click
from paths_cli.wizard.plugin_registration import register_installed_plugins
from paths_cli.wizard.two_state_tps import TWO_STATE_TPS_WIZARD
from paths_cli import OPSCommandPlugin

@click.command(
    'wizard',
    short_help="run wizard for setting up simulations",
)
def wizard():  # no-cov
    register_installed_plugins()
    TWO_STATE_TPS_WIZARD.run_wizard()


PLUGIN = OPSCommandPlugin(
    command=wizard,
    section="Simulation setup",
    requires_ops=(1, 0),
    requires_cli=(0, 3)
)

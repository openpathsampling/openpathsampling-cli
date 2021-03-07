import click
from paths_cli.wizard.two_state_tps import TWO_STATE_TPS_WIZARD

@click.command(
    'wizard',
    short_help="run wizard for setting up simulations",
)
def wizard():
    TWO_STATE_TPS_WIZARD.run_wizard()

CLI = wizard
SECTION = "Simulation setup"

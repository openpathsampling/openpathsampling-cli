import logging
import click

from paths_cli.plugin_management import FilePluginLoader, OPSPlugin

@click.command(
    'null-command',
    short_help="Do nothing (testing)"
)
def null_command():
    logger = logging.getLogger(__name__)
    logger.info("Running null command")

CLI = null_command
SECTION = "Workflow"

class NullCommandContext(object):
    """Context that registers/deregisters the null command (for tests)"""
    def __init__(self, cli):
        self.plugin = OPSPlugin(name="null-command",
                                location=__file__,
                                func=CLI,
                                section=SECTION,
                                plugin_type="file")

        cli._register_plugin(self.plugin)
        self.cli = cli

    def __enter__(self):
        self.cli._register_plugin(self.plugin)

    def __exit__(self, type, value, traceback):
        self.cli._deregister_plugin(self.plugin)

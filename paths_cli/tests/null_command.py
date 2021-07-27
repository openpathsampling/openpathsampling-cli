import logging
import click

from paths_cli.plugin_management import FilePluginLoader, OPSCommandPlugin

@click.command(
    'null-command',
    short_help="Do nothing (testing)"
)
def null_command():
    logger = logging.getLogger(__name__)
    logger.info("Running null command")

PLUGIN = OPSCommandPlugin(
    command=null_command,
    section="Workflow"
)

class NullCommandContext(object):
    """Context that registers/deregisters the null command (for tests)"""
    def __init__(self, cli):
        self.plugin = PLUGIN
        self.plugin.attach_metadata(location=__file__,
                                    plugin_type='file')

        cli._register_plugin(self.plugin)
        self.cli = cli

    def __enter__(self):
        self.cli._register_plugin(self.plugin)

    def __exit__(self, type, value, traceback):
        self.cli._deregister_plugin(self.plugin)

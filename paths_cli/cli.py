"""OpenPathSampling command line interface

This contains the "main" class/functions for running the OPS CLI.
"""
# builds off the example of MultiCommand in click's docs
import collections
import logging
import logging.config
import os
import pathlib

import click
# import click_completion
# click_completion.init()

from .plugin_management import FilePluginLoader, NamespacePluginLoader

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

class OpenPathSamplingCLI(click.MultiCommand):
    """Main class for the command line interface

    Most of the logic here is about handling the plugin infrastructure.
    """
    def __init__(self, *args, **kwargs):
        # the logic here is all about loading the plugins
        commands = str(pathlib.Path(__file__).parent.resolve() / 'commands')
        def app_dir_plugins(posix):
            return str(pathlib.Path(
                click.get_app_dir("OpenPathSampling", force_posix=posix)
            ).resolve() / 'cli-plugins')

        self.plugin_loaders = [
            FilePluginLoader(commands),
            FilePluginLoader(app_dir_plugins(posix=False)),
            FilePluginLoader(app_dir_plugins(posix=True)),
            NamespacePluginLoader('paths_cli_plugins')
        ]

        plugins = sum([loader() for loader in self.plugin_loaders], [])

        self._get_command = {}
        self._sections = collections.defaultdict(list)
        self.plugins = []
        for plugin in plugins:
            self._register_plugin(plugin)

        super(OpenPathSamplingCLI, self).__init__(*args, **kwargs)

    def _register_plugin(self, plugin):
        self.plugins.append(plugin)
        self._get_command[plugin.name] = plugin.func
        self._sections[plugin.section].append(plugin.name)

    def _deregister_plugin(self, plugin):
        # mainly used in testing
        self.plugins.remove(plugin)
        del self._get_command[plugin.name]
        self._sections[plugin.section].remove(plugin.name)

    def plugin_for_command(self, command_name):
        return {p.name: p for p in self.plugins}[command_name]

    def list_commands(self, ctx):
        return list(self._get_command.keys())

    def get_command(self, ctx, name):
        name = name.replace('_', '-')  # allow - or _ from user
        return self._get_command.get(name)

    def format_commands(self, ctx, formatter):
        sec_order = ['Simulation', 'Analysis', 'Miscellaneous', 'Workflow']
        for sec in sec_order:
            cmds = self._sections.get(sec, [])
            rows = []
            for cmd in cmds:
                command = self.get_command(ctx, cmd)
                if command is None:
                    continue
                rows.append((cmd, command.short_help or ''))

            if rows:
                with formatter.section(sec + " Commands"):
                    formatter.write_dl(rows)


_MAIN_HELP = """
OpenPathSampling is a Python library for path sampling simulations. This
command line tool facilitates common tasks when working with
OpenPathSampling. To use it, use one of the subcommands below. For example,
you can get more information about the pathsampling tool with:

    openpathsampling pathsampling --help
"""

@click.command(cls=OpenPathSamplingCLI, name="openpathsampling",
               help=_MAIN_HELP, context_settings=CONTEXT_SETTINGS)
@click.option('--log', type=click.Path(exists=True, readable=True),
              help="logging configuration file")
def main(log):
    if log:
        logging.config.fileConfig(log, disable_existing_loggers=False)
    # TODO: if log not given, check for logging.conf in .openpathsampling/

    logger = logging.getLogger(__name__)
    logger.debug("About to run command")  # TODO: maybe log invocation?

if __name__ == '__main__':  # no-cov
    main()

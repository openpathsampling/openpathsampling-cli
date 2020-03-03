"""OpenPathSampling command line interface

This contains the "main" class/functions for running the OPS CLI.
"""
# builds off the example of MultiCommand in click's docs
import collections
import logging
import logging.config
import os

import click
# import click_completion
# click_completion.init()

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

_POSSIBLE_PLUGIN_FOLDERS = [
    os.path.join(os.path.dirname(__file__), 'commands'),
    os.path.join(click.get_app_dir("OpenPathSampling"), 'cli-plugins'),
    os.path.join(click.get_app_dir("OpenPathSampling", force_posix=True),
                 'cli-plugins'),
]

OPSPlugin = collections.namedtuple("OPSPlugin",
                                   ['name', 'filename', 'func', 'section'])


class OpenPathSamplingCLI(click.MultiCommand):
    """Main class for the command line interface

    Most of the logic here is about handling the plugin infrastructure.
    """
    def __init__(self, *args, **kwargs):
        # the logic here is all about loading the plugins
        self.plugin_folders = []
        for folder in _POSSIBLE_PLUGIN_FOLDERS:
            if folder not in self.plugin_folders and os.path.exists(folder):
                self.plugin_folders.append(folder)

        plugin_files = self._list_plugin_files(self.plugin_folders)
        plugins = self._load_plugin_files(plugin_files)

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

    @staticmethod
    def _list_plugin_files(plugin_folders):
        def is_plugin(filename):
            return (
                filename.endswith(".py") and not filename.startswith("_")
                and not filename.startswith(".")
            )

        plugin_files = []
        for folder in plugin_folders:
            files = [os.path.join(folder, f) for f in os.listdir(folder)
                     if is_plugin(f)]
            plugin_files += files
        return plugin_files

    @staticmethod
    def _filename_to_command_name(filename):
        command_name = filename[:-3]  # get rid of .py
        command_name = command_name.replace('_', '-')  # commands use -
        return command_name

    @staticmethod
    def _load_plugin(name):
        ns = {}
        with open(name) as f:
            code = compile(f.read(), name, 'exec')
            eval(code, ns, ns)
        return ns['CLI'], ns['SECTION']

    def _load_plugin_files(self, plugin_files):
        plugins = []
        for full_name in plugin_files:
            _, filename = os.path.split(full_name)
            command_name = self._filename_to_command_name(filename)
            func, section = self._load_plugin(full_name)
            plugins.append(OPSPlugin(name=command_name, filename=full_name,
                                     func=func, section=section))
        return plugins

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
    cli()

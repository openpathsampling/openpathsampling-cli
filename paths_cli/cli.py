# builds off the example of MultiCommand in click's docs
import collections
import click
import os

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

plugin_folder = os.path.join(os.path.dirname(__file__), 'commands')

class OpenPathSamplingCLI(click.MultiCommand):
    def __init__(self, *args, **kwargs):
        self.plugin_folders = [
            os.path.join(os.path.dirname(__file__), 'commands'),
            os.path.join(click.get_app_dir("OpenPathSampling",
                                           force_posix=True),
                         'cli-plugins')
        ]
        self._get_command = {}
        self._sections = collections.defaultdict(list)
        plugin_files, command_list = self._list_plugins()
        for cmd, plugin_file in zip(command_list, plugin_files):
            command, section = self._load_plugin(plugin_file)
            self._get_command[cmd] = command
            self._sections[section].append(cmd)
        super(OpenPathSamplingCLI, self).__init__(*args, **kwargs)

    def _load_plugin(self, name):
        ns = {}
        fn = os.path.join(plugin_folder, name + '.py')
        with open(fn) as f:
            code = compile(f.read(), fn, 'exec')
            eval(code, ns, ns)
        return ns['CLI'], ns['SECTION']

    def _list_plugins(self):
        files = []
        commands = []
        for filename in os.listdir(plugin_folder):
            if filename.endswith('.py'):
                command = filename.replace('_', '-')
                files.append(filename[:-3])
                commands.append(command[:-3])
        return files, commands


    def list_commands(self, ctx):
        return list(self._get_command.keys())

    def get_command(self, ctx, name):
        name = name.replace('_', '-')  # auto alias to allow - or _
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


main_help="""
OpenPathSampling is a Python library for path sampling simulations. This
command line tool facilitates common tasks when working with
OpenPathSampling. To use it, use one of the subcommands below. For example,
you can get more information about the strip-snapshots (filesize reduction)
tool with:

    openpathsampling strip-snapshots --help
"""

def main():
    cli = OpenPathSamplingCLI(
        name="openpathsampling",
        help=main_help,
        context_settings=CONTEXT_SETTINGS
    )
    cli()

if __name__ == '__main__':
    main()
    # print("list commands:", cli.list_commands())

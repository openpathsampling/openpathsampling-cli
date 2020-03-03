import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from paths_cli.cli import *
from .null_command import NullCommandContext


class TestOpenPathSamplingCLI(object):
    # TODO: more thorough testing of private methods to find/register
    # plugins might be nice; so far we mainly focus on testing the API.
    # (Still have smoke tests covering everything, though.)
    def setup(self):
        def make_mock(name, helpless=False):
            mock = MagicMock(return_value=name)
            if helpless:
                mock.short_help = None
            else:
                mock.short_help = name + " help"
            return mock

        self.plugin_dict = {
            'foo': OPSPlugin(name='foo',
                             filename='foo.py',
                             func=make_mock('foo'),
                             section='Simulation'),
            'foo-bar': OPSPlugin(name='foo-bar',
                                 filename='foo_bar.py',
                                 func=make_mock('foobar', helpless=True),
                                 section='Miscellaneous')
        }
        self.fake_plugins = list(self.plugin_dict.values())
        mock_plugins = MagicMock(return_value=self.fake_plugins)
        with patch.object(OpenPathSamplingCLI, '_load_plugin_files',
                          mock_plugins):
            self.cli = OpenPathSamplingCLI()

    def test_plugins(self):
        assert self.cli.plugins == self.fake_plugins
        assert self.cli._sections['Simulation'] == ['foo']
        assert self.cli._sections['Miscellaneous'] == ['foo-bar']

    @pytest.mark.parametrize('name', ['foo', 'foo-bar'])
    def test_plugin_for_command(self, name):
        assert self.cli.plugin_for_command(name) == self.plugin_dict[name]

    def test_list_commands(self):
        assert self.cli.list_commands(ctx=None) == ['foo', 'foo-bar']

    @pytest.mark.parametrize('command', ['foo-bar', 'foo_bar'])
    def test_get_command(self, command):
        # this tests that renamings work
        cmd = self.cli.get_command(ctx=None, name=command)
        assert cmd() == 'foobar'

    def test_format_commands(self):
        class MockFormatter(object):
            def __init__(self):
                self.title = None
                self.contents = {}

            def section(self, title):
                self.title = title
                return MagicMock()

            def write_dl(self, rows):
                self.contents[self.title] = rows

        formatter = MockFormatter()
        # add a non-existent command; tests when get_command is None
        self.cli._sections['Workflow'] = ['baz']
        self.cli.format_commands(ctx=None, formatter=formatter)
        foo_row = ('foo', 'foo help')
        foobar_row = ('foo-bar', '')
        assert formatter.contents['Simulation Commands'] == [foo_row]
        assert formatter.contents['Miscellaneous Commands'] == [foobar_row]
        assert len(formatter.contents) == 2


@pytest.mark.parametrize('with_log', [True, False])
def test_main_log(with_log):
    logged_stdout = "About to run command\n"
    cmd_stdout = "Running null command\n"
    logfile_text = "\n".join([
        "[loggers]", "keys=root", "",
        "[handlers]", "keys=std", "",
        "[formatters]", "keys=default", "",
        "[formatter_default]", "format=%(message)s", "",
        "[handler_std]", "class=StreamHandler", "level=NOTSET",
        "formatter=default", "args=(sys.stdout,)", ""
        "[logger_root]", "level=DEBUG", "handlers=std"
    ])
    runner = CliRunner()
    invocation = {
        True: ['--log', 'logging.conf', 'null-command'],
        False: ['null-command']
    }[with_log]
    expected = {
        True: logged_stdout + cmd_stdout,
        False: ""
    }[with_log]
    with runner.isolated_filesystem():
        with open("logging.conf", mode='w') as log_conf:
            log_conf.write(logfile_text)

        with NullCommandContext(main):
            result = runner.invoke(main, invocation)
    found = result.stdout_bytes
    assert found.decode('utf-8') == expected

import pytest
from click.testing import CliRunner

import logging

from paths_cli.cli import *
from .null_command import NullCommandContext

class TestOpenPathSamplingCLI(object):
    def setup(self):
        # TODO: patch out the directory to fake the plugins
        self.cli = OpenPathSamplingCLI()

    def test_plugins(self):
        pytest.skip()
        pass

    def test_get_command(self):
        # test renamings
        pytest.skip()
        pass

    def test_format_commands(self):
        pytest.skip()
        # use a mock to get the formatter
        # test that it skips a section if it is empty
        pass

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
        False: cmd_stdout
    }[with_log]
    with runner.isolated_filesystem():
        with open("logging.conf", mode='w') as log_conf:
            log_conf.write(logfile_text)

        with NullCommandContext(main):
            result = runner.invoke(main, invocation)
    found = result.stdout_bytes
    assert found.decode('utf-8') == expected

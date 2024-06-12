from click.testing import CliRunner
from paths_cli.compiling.gendocs import *

from unittest import mock

@mock.patch('paths_cli.compiling.gendocs.load_config',
            mock.Mock(return_value={}))
def test_main():
    # this is a smoke test, just to ensure that it doesn't crash;
    # functionality testing is in the _gendocs directory
    runner = CliRunner()
    with runner.isolated_filesystem():
        _ = runner.invoke(main, 'fake_config.yml', '--stdout')


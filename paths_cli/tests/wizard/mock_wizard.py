from paths_cli.wizard.wizard import Wizard
import mock

def make_mock_wizard(inputs):
    wizard = Wizard([])
    wizard.console.input = mock.Mock(return_value=inputs)
    return wizard

def make_mock_retry_wizard(inputs):
    wizard = Wizard([])
    wizard.console.input = mock.Mock(side_effect=inputs)
    return wizard

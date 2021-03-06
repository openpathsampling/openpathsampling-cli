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

class MockConsole:
    def __init__(self, inputs=None):
        if isinstance(inputs, str):
            inputs = [inputs]
        elif inputs is None:
            inputs = []
        self.inputs = inputs
        self._input_iter = iter(inputs)
        self.log = []
        self.width = 80
        self.input_call_count = 0

    def print(self, content=""):
        self.log.append(content)

    def input(self, content):
        self.input_call_count += 1
        user_input = next(self._input_iter)
        self.log.append(content + " " + user_input)
        return user_input

    @property
    def log_text(self):
        return "\n".join(self.log)

def mock_wizard(inputs):
    wizard = Wizard([])
    console = MockConsole(inputs)
    wizard.console = console
    return wizard



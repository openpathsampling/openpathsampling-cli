import pytest

from paths_cli.wizard.helper import *
from paths_cli.wizard.helper import _LONG_EVAL_HELP

def test_raise_quit():
    with pytest.raises(QuitWizard):
        raise_quit("foo", None)

def test_restart():
    with pytest.raises(RestartObjectException):
        raise_restart("foo", None)

def test_force_exit():
    with pytest.raises(SystemExit):
        force_exit("foo", None)

class TestEvalHelperFunc:
    def setup_method(self):
        self.param_helper = {
            'str': "help_string",
            'method': lambda help_args, context: f"help_{help_args}"
        }
        self.expected = {
            'str': "help_string",
            'method': "help_foo"
        }

    @pytest.mark.parametrize('helper_type', ['str', 'method'])
    def test_call(self, helper_type):
        help_func = EvalHelperFunc(self.param_helper[helper_type])
        help_str = help_func("foo")
        assert self.expected[helper_type] in help_str
        assert "ask for help with '?eval'" in help_str

    @pytest.mark.parametrize('helper_type', ['str', 'method'])
    def test_call_eval(self, helper_type):
        help_func = EvalHelperFunc(self.param_helper[helper_type])
        assert help_func("eval") == _LONG_EVAL_HELP

class TestHelper:
    def setup_method(self):
        self.helper = Helper(help_func=lambda s, ctx: s)

    def test_help_string(self):
        # if the helper "function" is a string, return that string whether
        # or not additional arguments to help are given
        helper = Helper(help_func="a string")
        assert helper("?") == "a string"
        assert helper("?foo") == "a string"

    def test_help_with_args(self):
        # if the helper can process arguments, do so (our example return the
        # input)
        assert self.helper("?foo") == "foo"

    def test_command_help_empty(self):
        # when calling help with "?!", get the list of commands
        assert "The following commands can be used" in self.helper("?!")

    @pytest.mark.parametrize('inp', ["?!q", "?!quit"])
    def test_command_help_for_command(self, inp):
        # when calling help on a specific command, get the help for that
        # command
        assert "The !quit command" in self.helper(inp)

    def test_command_help_no_such_command(self):
        # if asking for help on an unknown command, report that there is no
        # help available for it
        assert "No help for" in self.helper("?!foo")

    @pytest.mark.parametrize('inp', ["!q", "!quit"])
    def test_run_command_quit(self, inp):
        # run the quit command when asked to
        with pytest.raises(QuitWizard):
            self.helper(inp)

    @pytest.mark.parametrize('inp', ["!!q", "!!quit"])
    def test_run_command_force_quit(self, inp):
        # run the force quit command when asked to
        with pytest.raises(SystemExit):
            self.helper(inp)

    def test_run_command_restart(self):
        # run the restart command when asked to
        with pytest.raises(RestartObjectException):
            self.helper("!restart")

    def test_run_command_unknown(self):
        # unknown command names should just report an unknown command
        assert "Unknown command" in self.helper("!foo")

    def test_run_command_no_argument(self):
        assert "Please provide a command. The following" in self.helper("!")

    def test_empty_helper(self):
        empty = Helper(help_func=None)
        assert "no help available" in empty("?")
        assert "no help available" in empty("?foo")

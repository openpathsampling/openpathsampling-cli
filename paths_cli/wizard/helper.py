import sys
from .errors import RestartObjectException


class QuitWizard(BaseException):
    """Exception raised when user expresses desire to quit the wizard"""


# the following command functions take cmd and ctx -- future commands might
# use the full command text or the context internally.

def raise_quit(cmd, ctx):
    """Command function to quit the wizard (with option to save).
    """
    raise QuitWizard()


def raise_restart(cmd, ctx):
    """Command function to restart the current object.
    """
    raise RestartObjectException()


def force_exit(cmd, ctx):
    """Command function to force immediate exit.
    """
    print("Exiting...")
    sys.exit()


HELPER_COMMANDS = {
    'q': raise_quit,
    'quit': raise_quit,
    '!q': force_exit,
    '!quit': force_exit,
    'restart': raise_restart,
    'fuck': raise_restart,  # easter egg ;-)
    # TODO: add ls, perhaps others?
}

_QUIT_HELP = ("The !quit command (or !q) will quit the wizard, but only "
              "after it checks whether you want to save the objects you've "
              "created.")
_FORCE_QUIT_HELP = ("The !!quit command (or !!q) will immediately force "
                    "quit the wizard.")
_RESTART_HELP = ("The !restart command will restart the creation of the "
                 "current object in the wizard. Note that for objects that "
                 "contain other objects (such as state definitions, which "
                 "may be made of multiple volumes) this will restart from "
                 "the outermost object (e.g., the state).")
COMMAND_HELP_STR = {
    'q': _QUIT_HELP,
    'quit': _QUIT_HELP,
    '!q': _FORCE_QUIT_HELP,
    '!quit': _FORCE_QUIT_HELP,
    'restart': _RESTART_HELP,
}


_SHORT_EVAL_HELP = ("You can use expression evaluation with this "
                    "parameter! For details, ask for help with '?eval'.")
_LONG_EVAL_HELP = (
    "You can use a Python expression to create the value for this "
    "parameter. However, there are a few limitations:\n\n",
    " * You're limited to a single expression. That basically means a "
    "single line of Python, and no control structures like for loops.\n\n"
    " * You can't import any libraries. However, math and numpy are "
    "included (use numpy as 'np').\n\n"
    "The expression evaluator means that you can use simple expressions "
    "as input. For example, say you wanted 100 degrees in radians. You "
    "could just type\n\n"
    "  100 * np.pi / 180\n\n"
    "as your input for the parameter."
)


class EvalHelperFunc:
    """Helper function (input to :class:`.Helper`) for evaluated parameters.

    Parameters
    ----------
    param_helper : str or Callable[str, dict] -> str
        help string or method that takes arguments and context dict and
        results the help string
    """
    def __init__(self, param_helper):
        if isinstance(param_helper, str):
            helper = lambda wizard, context: param_helper
        else:
            helper = param_helper
        self.helper = helper

    def __call__(self, helpargs, context=None):
        if helpargs == "eval":
            return _LONG_EVAL_HELP
        return self.helper(helpargs, context) + "\n\n" + _SHORT_EVAL_HELP


class Helper:
    """Manage help and command passing on command line.

    Any user input beginning with "?" or "!" is passed to the helper. Input
    beginning with "!" is used to call commands, which allow the user to
    interact with the system or to force control flow that isn't built into
    the wizard. Input beginning with "?" is interpreted as a request for
    help, and the text after "?" is passed from the Helper to its help_func
    (or to the tools for help about commands.)

    Parameters
    ----------
    help_func : str or Callable[str, dict] -> str
        If a Callable, it must take the user-provided string and the context
        dict. If a string, the help will always return that string for any
        user-provided arguments.
    """
    def __init__(self, help_func):
        # TODO: generalize to get help on specific aspects?
        if isinstance(help_func, str):
            text = str(help_func)
            help_func = lambda args, ctx: text

        self.helper = help_func
        self.commands = HELPER_COMMANDS.copy()  # allows per-instance custom
        self.command_help_str = COMMAND_HELP_STR.copy()
        self.listed_commands = ['quit', '!quit', 'restart']

    def _command_help(self, help_args, context):
        """Handle help for commands.

        Invoked if user input begins with "?!"
        """
        if help_args == "":
            result = "The following commands can be used:\n"
            result += "\n".join([f"* !{cmd}"
                                 for cmd in self.listed_commands])
        else:
            try:
                result = self.command_help_str[help_args]
            except KeyError:
                result = f"No help for !{help_args}."

        return result

    def _run_command(self, command, context):
        """Runs a the given command.

        Invoked if user input begins with "!"
        """
        cmd_split = command.split()
        try:
            key = cmd_split[0]
        except IndexError:
            return ("Please provide a command. "
                    + self._command_help("", context))

        args = " ".join(cmd_split[1:])
        try:
            cmd = self.commands[key]
        except KeyError:
            return f"Unknown command: {key}"

        return cmd(args, context)

    def _get_help(self, help_args, context):
        """Get help from either command help or user-provided help.

        Invoked if user input begins with "?"
        """
        if help_args != "" and help_args[0] == '!':
            return self._command_help(help_args[1:], context)

        if self.helper is None:
            return "Sorry, no help available here."

        return self.helper(help_args, context)

    def __call__(self, user_input, context=None):
        starter = user_input[0]
        args = user_input[1:]
        func = {'?': self._get_help,
                '!': self._run_command}[starter]
        return func(args, context)

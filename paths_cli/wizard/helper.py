from .errors import RestartObjectException

class QuitWizard(BaseException):
    pass

def raise_quit(cmd, ctx):
    raise QuitWizard()

def raise_restart(cmd, ctx):
    raise RestartObjectException()

def force_exit(cmd, ctx):
    print("Exiting...")
    exit()

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

class Helper:
    def __init__(self, help_func):
        # TODO: generalize to get help on specific aspects?
        if isinstance(help_func, str):
            text = str(help_func)
            help_func = lambda args, ctx: text
        self.helper = help_func
        self.commands = HELPER_COMMANDS.copy()  # allows per-instance custom
        self.command_help_str = COMMAND_HELP_STR.copy()
        self.listed_commands = ['quit', '!quit', 'restart']

    def command_help(self, help_args, context):
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


    def run_command(self, command, context):
        cmd_split = command.split()
        try:
            key = cmd_split[0]
        except IndexError:
            return ("Please provide a command. "
                    + self.command_help("", context))

        args = " ".join(cmd_split[1:])
        try:
            cmd = self.commands[key]
        except KeyError:
            return f"Unknown command: {key}"

        return cmd(args, context)

    def get_help(self, help_args, context):
        # TODO: add default help (for ?!, etc)
        if help_args != "" and help_args[0] == '!':
            return self.command_help(help_args[1:], context)

        if self.helper is None:
            return "Sorry, no help available here."

        return self.helper(help_args, context)

    def __call__(self, user_input, context=None):
        starter = user_input[0]
        args = user_input[1:]
        func = {'?': self.get_help,
                '!': self.run_command}[starter]
        return func(args, context)

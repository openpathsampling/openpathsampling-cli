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
    'restart': raise_restart,
    'fuck': raise_restart,  # easter egg ;-)
    # TODO: add ls, perhaps others?
}


class Helper:
    def __init__(self, help_func):
        # TODO: generalize to get help on specific aspects?
        if isinstance(help_func, str):
            text = str(help_func)
            help_func = lambda args, ctx: text
        self.helper = help_func
        self.commands = HELPER_COMMANDS.copy()  # allows per-instance custom

    def run_command(self, command, context):
        cmd_split = command.split()
        key = cmd_split[0]
        args = " ".join(cmd_split[1:])
        return self.commands[key](args, context)

    def get_help(self, help_args, context):
        return self.helper(help_args, context)

    def __call__(self, user_input, context=None):
        starter = user_input[0]
        args = user_input[1:]
        func = {'?': self.get_help,
                '!': self.run_command}[starter]
        return func(args, context)



class ImpossibleError(Exception):
    def __init__(self, msg=None):
        if msg is None:
            msg = "Something went really wrong. You should never see this."
        super().__init__(msg)

class RestartObjectException(BaseException):
    pass

def not_installed(package, obj_type):
    retry = wizard.ask("Hey, it looks like you don't have {package} "
                       "installed. Do you want to try a different "
                       "{obj_type}, or do you want to quit?",
                       options=["[R]etry", "[Q]uit"])
    if retry == 'r':
        return
    elif retry == 'q':
        exit()
    else:
        raise ImpossibleError()


FILE_LOADING_ERROR_MSG = ("Sorry, something went wrong when loading that "
                          "file.")

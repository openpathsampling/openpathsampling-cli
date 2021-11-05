class ImpossibleError(Exception):
    """Error to throw for sections that should be unreachable code"""
    def __init__(self, msg=None):
        if msg is None:
            msg = "Something went really wrong. You should never see this."
        super().__init__(msg)


class RestartObjectException(BaseException):
    """Exception to indicate the restart of an object.

    Raised when the user issues a command to cause an object restart.
    """
    pass


def not_installed(wizard, package, obj_type):
    """Behavior when an integration is not installed.

    In actual practice, this calling code should ensure this doesn't get
    used. However, we keep it around as a defensive practice.

    Parameters
    ----------
    package : str
        name of the missing package
    obj_type : str
        name of the object category that would have been created
    """
    retry = wizard.ask(f"Hey, it looks like you don't have {package} "
                       "installed. Do you want to try a different "
                       f"{obj_type}, or do you want to quit?",
                       options=["[r]etry", "[q]uit"])
    if retry == 'r':
        raise RestartObjectException()
    if retry == 'q':
        # TODO: maybe raise QuitWizard instead?
        exit()
    raise ImpossibleError()  # -no-cov-


FILE_LOADING_ERROR_MSG = ("Sorry, something went wrong when loading that "
                          "file.")

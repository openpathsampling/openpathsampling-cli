class InputError(Exception):
    """Raised when users provide bad input in files/interactive sessions.
    """
    @classmethod
    def invalid_input(cls, value, attr):
        msg = f"'{value}' is not a valid input for {attr}"
        return cls(msg)

    @classmethod
    def unknown_name(cls, type_name, name):
        return cls(f"Unable to find object named {name} in {type_name}")

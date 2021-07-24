class InputError(Exception):
    @classmethod
    def invalid_input(cls, value, attr, type_name=None, name=None):
        msg = f"'{value}' is not a valid input for {attr}"
        if type_name is not None:
            msg += f" in {type_name}"
        if name is not None:
            msg += f" named {name}"
        return cls(msg)

    @classmethod
    def unknown_name(cls, type_name, name):
        return cls(f"Unable to find object named {name} in {type_name}")


from paths_cli.parsing.tools import custom_eval
import importlib

from paths_cli.wizard.helper import Helper

NO_DEFAULT = object()

NO_PARAMETER_LOADED = object()

CUSTOM_EVAL_ERROR = "Sorry, I couldn't understand the input '{user_str}'"

def do_import(fully_qualified_name):
    dotted = fully_qualified_name.split('.')
    thing = dotted[-1]
    module = ".".join(dotted[:-1])
    # stole this from SimStore
    mod = importlib.import_module(module)
    result = getattr(mod, thing)
    return result


class Parameter:
    def __init__(self, name, load_method):
        self.name = name
        self.load_method = load_method

    def __call__(self, wizard):
        result = NO_PARAMETER_LOADED
        while result is NO_PARAMETER_LOADED:
            result = self.load_method(wizard)
        return result


class SimpleParameter(Parameter):
    def __init__(self, name, ask, loader, helper=None, error=None,
                 default=NO_DEFAULT, autohelp=False):
        super().__init__(name, self._load_method)
        self.ask = ask
        self.loader = loader
        if helper is None:
            helper = Helper("Sorry, no help is available for this "
                            "parameter.")
        if not isinstance(helper, Helper):
            helper = Helper(helper)
        self.helper = helper

        if error is None:
            error = "Something went wrong processing the input '{user_str}'"
        self.error = error
        self.default = default
        self.autohelp = autohelp

    def _process_input(self, wizard, user_str):
        obj = NO_PARAMETER_LOADED
        if user_str[0] in ['?', '!']:
            wizard.say(self.helper(user_str))
            return NO_PARAMETER_LOADED

        try:
            obj = self.loader(user_str)
        except Exception as e:
            wizard.exception(self.error.format(user_str=user_str), e)
            if self.autohelp:
                wizard.say(self.helper("?"))

        return obj

    def _load_method(self, wizard):
        user_str = wizard.ask(self.ask)
        result = self._process_input(wizard, user_str)
        return result


def load_custom_eval(type_=None):
    if type_ is None:
        type_ = lambda x: x
    def parse(input_str):
        return type_(custom_eval(input_str))

    return parse


class InstanceBuilder:
    """

    Parameters
    ----------
    parameters: List[:class:`.Parameter`]
    category: str
    cls: Union[str, type]
    intro: str
    help_str: str
    remapper: Callable[dict, dict]
    make_summary: Callable[dict, str]
        Function to create an output string to summarize the object that has
        been created. Optional.
    """
    def __init__(self, parameters, category, cls, intro=None, help_str=None,
                 remapper=None, make_summary=None):
        self.parameters = parameters
        self.param_dict = {p.name: p for p in parameters}
        self.category = category
        self._cls = cls
        self.intro = intro
        self.help_str = help_str
        if remapper is None:
            remapper = lambda x: x
        self.remapper = remapper
        if make_summary is None:
            make_summary = lambda dct: None
        self.make_summary = make_summary

    @property
    def cls(self):
        # trick to delay slow imports
        if isinstance(self._cls, str):
            self._cls = do_import(self._cls)
        return self._cls

    def __call__(self, wizard):
        if self.intro is not None:
            wizard.say(self.intro)

        param_dict = {p.name: p(wizard) for p in self.parameters}
        kwargs = self.remapper(param_dict)
        return self.cls(**kwargs)

from paths_cli.compiling.tools import custom_eval
import importlib
from collections import namedtuple

from paths_cli.wizard.helper import Helper
from paths_cli.compiling.root_compiler import _CategoryCompilerProxy
from paths_cli.wizard.standard_categories import get_category_info

NO_DEFAULT = object()

NO_PARAMETER_LOADED = object()

ProxyParameter = namedtuple(
    'ProxyParameter',
    ['name', 'ask', 'helper', 'default', 'autohelp', 'summarize'],
    defaults=[None, NO_DEFAULT, False, None]
)

class WizardParameter:
    """Load a single parameter from the wizard.

    Parameters
    ----------
    name : str
        name of this parameter
    ask : List[str]
        list of strings that the wizard should use to ask the user for
        input. These can be formatted with a provided ``context`` dict.
    loader : Callable
        method to create parameter from user input string
    helper : Union[`:class:.Helper`, str]
        method to provide help for this parameter
    default : Any
        default value of this parameter; ``NO_DEFAULT`` if no default exists
    autohelp : bool
        if True, bad input automatically causes the help information to be
        shown. Default False.
    summarize : Callable
        method to provide summary of created output.
    """
    def __init__(self, name, ask, loader, *, helper=None, default=NO_DEFAULT,
                 autohelp=False, summarize=None):
        self.name = name
        self.ask = ask
        self.loader = loader
        self.helper = helper
        self.default = default
        self.autohelp = autohelp
        if summarize is None:
            summarize = lambda obj: str(obj)
        self.summarize = summarize

    @classmethod
    def from_proxy(cls, proxy, compiler_plugin):
        """Create a parameter from a proxy parameter a compiler plugin.

        Parameters
        ----------
        proxy : :class:`.ProxyParameter`
            proxy with wizard-specific information for user interaction
        compiler_plugin : :class:`.InstanceCompilerPlugin`
            the compiler plugin to make objects of this type
        """
        loader_dict = {p.name: p.loader for p in compiler_plugin.parameters}
        dct = proxy._asdict()
        loader = loader_dict[proxy.name]
        if isinstance(loader, _CategoryCompilerProxy):
            # TODO: can this import now be moved to top of file?
            from paths_cli.wizard.plugin_registration import get_category_wizard
            category = loader.category
            dct['loader'] = get_category_wizard(category)
            dct['ask'] = get_category_info(category).singular
            dct['store_name'] = get_category_info(category).storage
            cls = ExistingObjectParameter
        else:
            dct['loader'] = loader
        return cls(**dct)

    def __call__(self, wizard, context):
        obj = NO_PARAMETER_LOADED
        ask = self.ask.format(**context)
        while obj is NO_PARAMETER_LOADED:
            obj = wizard.ask_load(ask, self.loader, self.helper,
                                  autohelp=self.autohelp)
        return obj


class ExistingObjectParameter(WizardParameter):
    """Special parameter type for parameters created by wizards.

    This should only be created as part of the
    :method:`.WizardParameter.from_proxy` method; client code should not use
    this directly.
    """
    def __init__(self, name, ask, loader, store_name, *, helper=None,
                 default=NO_DEFAULT, autohelp=False, summarize=None):
        super().__init__(name=name, ask=ask, loader=loader, helper=helper,
                         default=default, autohelp=autohelp,
                         summarize=summarize)
        self.store_name = store_name

    @classmethod
    def from_proxy(cls, proxy, compiler_plugin):
        raise NotImplementedError()

    def __call__(self, wizard, context):
        ask = self.ask.format(**context)
        obj = wizard.obj_selector(self.store_name, ask, self.loader)
        return obj


class FromWizardPrerequisite:
    """Load prerequisites from the wizard.
    """
    def __init__(self, name, create_func, category, n_required, *,
                 obj_name=None, store_name=None, say_select=None,
                 say_create=None, say_finish=None, load_func=None):
        self.name = name
        self.create_func = create_func
        self.category = category
        if obj_name is None:
            obj_name = get_category_info(category).singular
        if store_name is None:
            store_name = get_category_info(category).storage

        self.obj_name = obj_name
        self.store_name = store_name
        self.n_required = n_required
        self.say_select = say_select
        self.say_create = say_create
        self.say_finish = say_finish
        if load_func is None:
            load_func = lambda x: x

        self.load_func = load_func

    def create_new(self, wizard):
        if self.say_create:
            wizard.say(self.say_create)
        obj = self.create_func(wizard)
        wizard.register(obj, self.obj_name, self.store_name)
        result = self.load_func(obj)
        return result

    def get_existing(self, wizard):
        all_objs = list(getattr(wizard, self.store_name).values())
        results = [self.load_func(obj) for obj in all_objs]
        return results

    def select_existing(self, wizard):
        obj = wizard.obj_selector(self.store_name, self.obj_name,
                                  self.create_func)
        return [self.load_func(obj)]

    def __call__(self, wizard):
        n_existing = len(getattr(wizard, self.store_name))
        if n_existing == self.n_required:
            # early return in this case (return silently)
            return {self.name: self.get_existing(wizard)}
        elif n_existing > self.n_required:
            dct = {self.name: self.select_existing(wizard)}
        else:
            objs = []
            while len(getattr(wizard, self.store_name)) < self.n_required:
                objs.append(self.create_new(wizard))
            dct = {self.name: objs}

        if self.say_finish:
            wizard.say(self.say_finish)
        return dct

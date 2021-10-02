from paths_cli.compiling.tools import custom_eval
import importlib
from collections import namedtuple

from paths_cli.wizard.helper import Helper

NO_DEFAULT = object()

NO_PARAMETER_LOADED = object()

ProxyParameter = namedtuple(
    'ProxyParameter',
    ['name', 'ask', 'helper', 'default', 'autohelp', 'summarize'],
    defaults=[None, NO_DEFAULT, False, None]
)

class WizardParameter:
    def __init__(self, name, ask, loader, helper=None, default=NO_DEFAULT,
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
        loader_dict = {p.name: p.loader for p in compiler_plugin.parameters}
        dct = proxy._asdict()
        dct['loader'] = loader_dict[proxy.name]
        return cls(**dct)

    def __call__(self, wizard):
        obj = NO_PARAMETER_LOADED
        while obj is NO_PARAMETER_LOADED:
            obj = wizard.ask_load(self.ask, self.loader, self.helper,
                                  autohelp=self.autohelp)
        return obj


class WizardObjectPlugin:
    def __init__(self, name, category, builder, prerequisite=None,
                 intro=None, description=None, summary=None):
        self.name = name
        self.category = category
        self.builder = builder
        self.prerequisite = prerequisite
        self.intro = intro
        self.description = description
        self._summary = summary  # func to summarize

    def summary(self, obj):
        if self._summary:
            return self._summary(obj)
        else:
            return "  " + str(obj)

    def __call__(self, wizard):
        if self.intro is not None:
            wizard.say(self.intro)

        if self.prerequisite is not None:
            prereqs = self.prerequisite(wizard)
        else:
            prereqs = {}

        result = self.builder(wizard, prereqs)
        wizard.say("Here's what we'll create:\n" + self.summary(result))
        return result


class WizardParameterObjectPlugin(WizardObjectPlugin):
    def __init__(self, name, category, parameters, builder, *,
                 prerequisite=None, intro=None, description=None):
        super().__init__(name=name, category=category, builder=self._build,
                         prerequisite=prerequisite, intro=intro,
                         description=description)
        self.parameters = parameters
        self.build_func = builder
        self.proxy_parameters = []  # non-empty if created from proxies

    @classmethod
    def from_proxies(cls, name, category, parameters, compiler_plugin,
                     prerequisite=None, intro=None, description=None):
        """
        Use the from_proxies method if you already have a compiler plugin.
        """
        params = [WizardParameter.from_proxy(proxy, compiler_plugin)
                  for proxy in parameters]
        obj = cls(name=name,
                  category=category,
                  parameters=params,
                  builder=compiler_plugin.builder,
                  prerequisite=prerequisite,
                  intro=intro,
                  description=description)
        obj.proxy_parameters = parameters
        return obj

    def _build(self, wizard, prereqs):
        dct = dict(prereqs)  # shallow copy
        dct.update({p.name: p(wizard) for p in self.parameters})
        result = self.build_func(**dct)
        return result


class FromWizardPrerequisite:
    """Load prerequisites from the wizard.
    """
    def __init__(self, name, create_func, category, obj_name, n_required,
                 say_select=None, say_create=None, say_finish=None,
                 load_func=None):
        self.name = name
        self.create_func = create_func
        self.category = category
        self.obj_name = obj_name
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
        wizard.register(obj, self.obj_name, self.category)
        result = self.load_func(obj)
        return result

    def get_existing(self, wizard):
        all_objs = list(getattr(wizard, self.category).values())
        results = [self.load_func(obj) for obj in all_objs]
        return results

    def select_existing(self, wizard):
        pass

    def __call__(self, wizard):
        n_existing = len(getattr(wizard, self.category))
        if n_existing == self.n_required:
            # early return in this case (return silently)
            return {self.name: self.get_existing(wizard)}
        elif n_existing > self.n_required:
            dct = {self.name: self.select_existing(wizard)}
        else:
            objs = []
            while len(getattr(wizard, self.category)) < self.n_required:
                objs.append(self.create_new(wizard))
            dct = {self.name: objs}

        if self.say_finish:
            wizard.say(self.say_finish)
        return dct

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

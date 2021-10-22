from paths_cli.plugin_management import OPSPlugin
from paths_cli.wizard.standard_categories import get_category_info
from paths_cli.wizard.load_from_ops import load_from_ops
from paths_cli.wizard.parameters import WizardParameter
from paths_cli.wizard.helper import Helper
import textwrap

_WIZARD_KWONLY = """
    prerequisite : Callable
        method to use to create any objects required for the target object
    intro : Union[Callable, str]
        method to produce the intro text for the wizard to say
    description : str
        description to be used in help functions when this plugin is a
        choice
    summary : Callable
        method to create the summary string describing the object that is
        created
    requires_ops : Tuple[int, int]
        version of OpenPathSampling required for this plugin
    requires_cli : Tuple[int, int]
        version of the OpenPathSampling CLI required for this plugin
"""



class LoadFromOPS(OPSPlugin):
    def __init__(self, category, obj_name=None, store_name=None,
                 requires_ops=(1,0), requires_cli=(0,3)):
        super().__init__(requires_ops, requires_cli)
        self.category = category
        self.name = "Load existing from OPS file"
        if obj_name is None:
            obj_name = get_category_info(category).singular

        if store_name is None:
            store_name = get_category_info(category).storage

        self.obj_name = obj_name
        self.store_name = store_name

    def __call__(self, wizard):
        return load_from_ops(wizard, self.store_name, self.obj_name)


class WizardObjectPlugin(OPSPlugin):
    """Base class for wizard plugins to create OPS objects.

    This allows full overrides of the entire object creation process. For
    simple objects, see :class:`.WizardParameterObjectPlugin`, which makes
    the easiest cases much easier.

    Parameters
    ----------
    name : str
        name of this object type
    category : str
        name of the category to which this object belongs
    builder : Callable
        method used to build object based on loaded data
    """ + _WIZARD_KWONLY
    def __init__(self, name, category, builder, *, prerequisite=None,
                 intro=None, description=None, summary=None,
                 requires_ops=(1,0), requires_cli=(0,3)):
        super().__init__(requires_ops, requires_cli)
        self.name = name
        self.category = category
        self.builder = builder
        self.prerequisite = prerequisite
        self.intro = intro
        self.description = description
        self._summary = summary  # func to summarize

    def default_summarize(self, wizard, context, result):
        return [f"Here's what we'll make:\n  {str(result)}"]

    def get_summary(self, wizard, context, result):
        # TODO: this pattern has been repeated -- make it a function (see
        # also get_intro)
        summarize = context.get('summarize', self._summary)
        if summarize is None:
            summarize = self.default_summarize

        try:
            summary = summarize(wizard, context, result)
        except TypeError:
            summary = summarize

        if summary is None:
            summary = []

        if isinstance(summary, str):
            summary = [summary]

        return summary

    def __call__(self, wizard, context=None):
        if context is None:
            context = {}

        if self.intro is not None:
            wizard.say(self.intro)

        if self.prerequisite is not None:
            prereqs = self.prerequisite(wizard)
        else:
            prereqs = {}

        result = self.builder(wizard, prereqs)
        summary = self.get_summary(wizard, context, result)
        for line in summary:
            wizard.say(line)
        return result

    def __repr__(self):
        return (f"{self.__class__.__name__}(name={self.name}, "
                f"category={self.category})")


class WizardParameterObjectPlugin(WizardObjectPlugin):
    """Object plugin that uses :class:`.WizardParameter`

    Parameters
    ----------
    name : str
        name of this object type
    category : str
        name of the category to which this object belongs
    parameters : List[:class:`.WizardParameter`]
        parameters used in this object
    builder : Callable
        method used to build object based on loaded parameters -- note, this
        must take the names of the parameters as keywords.
    """ + _WIZARD_KWONLY
    def __init__(self, name, category, parameters, builder, *,
                 prerequisite=None, intro=None, description=None,
                 summary=None, requires_ops=(1, 0), requires_cli=(0, 3)):
        super().__init__(name=name, category=category, builder=self._build,
                         prerequisite=prerequisite, intro=intro,
                         description=description, summary=summary,
                         requires_ops=requires_ops,
                         requires_cli=requires_cli)
        self.parameters = parameters
        self.build_func = builder
        self.proxy_parameters = []  # non-empty if created from proxies

    @classmethod
    def from_proxies(cls, name, category, parameters, compiler_plugin,
                     prerequisite=None, intro=None, description=None,
                     summary=None, requires_ops=(1,0), requires_cli=(0,3)):
        """
        Create plugin from proxy parameters and existing compiler plugin.

        This method facilitates reuse of plugins used in the compiler,
        avoiding repeating code to create the instance from user input.

        Parameters
        ----------
        name : str
            name of this object type
        category : str
            name of the category to which this object belongs
        parameters : List[ProxyParameter]
            proxy parameters containing wizard-specific user interaction
            infomration. These must have names that correspond to the names
            of the ``compiler_plugin``.
        compiler_plugin : :class:`.InstanceCompilerPlugin`
            the compiler plugin to use to create the object
        """ + textwrap.indent(_WIZARD_KWONLY, ' ' * 4)
        params = [WizardParameter.from_proxy(proxy, compiler_plugin)
                  for proxy in parameters]
        obj = cls(name=name, category=category, parameters=params,
                  builder=compiler_plugin.builder,
                  prerequisite=prerequisite, intro=intro,
                  description=description, summary=summary,
                  requires_ops=requires_ops, requires_cli=requires_cli)
        obj.proxy_parameters = parameters
        return obj

    def _build(self, wizard, prereqs):
        dct = dict(prereqs)
        context = {'obj_dict': dct}
        for param in self.parameters:
            dct[param.name] = param(wizard, context)
        # dct.update({p.name: p(wizard) for p in self.parameters})
        result = self.build_func(**dct)
        return result


class CategoryHelpFunc:
    def __init__(self, category, basic_help=None):
        self.category = category
        if basic_help is None:
            basic_help = f"Sorry, no help available for {category.name}."
        self.basic_help = basic_help

    def __call__(self, help_args, context):
        if not help_args:
            return self.basic_help
        help_dict = {}
        for num, (name, obj) in enumerate(self.category.choices.items()):
            try:
                help_str = obj.description
            except Exception:
                help_str = f"Sorry, no help available for '{name}'."
            help_dict[str(num+1)] = help_str
            help_dict[name] = help_str

        try:
            result = help_dict[help_args]
        except KeyError:
            result = None
        return result


class WrapCategory(OPSPlugin):
    def __init__(self, name, ask, helper=None, intro=None, set_context=None,
                 requires_ops=(1,0), requires_cli=(0,3)):
        super().__init__(requires_ops, requires_cli)
        self.name = name
        if isinstance(intro, str):
            intro = [intro]
        self.intro = intro
        self.ask = ask
        self._set_context = set_context
        if helper is None:
            helper = Helper(CategoryHelpFunc(self))
        if isinstance(helper, str):
            helper = Helper(CategoryHelpFunc(self, helper))

        self.helper = helper
        self.choices = {}

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"

    def set_context(self, wizard, context, selected):
        if self._set_context:
            return self._set_context(wizard, context, selected)
        else:
            return context

    def register_plugin(self, plugin):
        self.choices[plugin.name] = plugin

    def get_intro(self, wizard, context):
        intro = context.get('intro', self.intro)

        try:
            intro = intro(wizard, context)
        except TypeError:
            pass

        if intro is None:
            intro = []

        return intro

    def get_ask(self, wizard, context):
        try:
            ask = self.ask(wizard, context)
        except TypeError:
            ask = self.ask.format(**context)
        return ask

    def __call__(self, wizard, context=None):
        if context is None:
            context = {}

        intro = self.get_intro(wizard, context)

        for line in intro:
            wizard.say(line)

        ask = self.get_ask(wizard, context)

        selected = wizard.ask_enumerate_dict(ask, self.choices,
                                             self.helper)

        new_context = self.set_context(wizard, context, selected)
        obj = selected(wizard, new_context)
        return obj


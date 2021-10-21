NO_PARAMETER_LOADED = object()

from .helper import Helper
from paths_cli.plugin_management import OPSPlugin

# class WrapCompilerWizardPlugin:
#     def __init__(self, name, category, parameters, compiler_plugin,
#                  prerequisite=None, intro=None, description=None):
#         self.name = name
#         self.parameters = parameters
#         self.compiler_plugin = compiler_plugin
#         self.prerequisite = prerequisite
#         self.intro = intro
#         self.description = description
#         loaders = {p.name: p.loader for p in self.compiler_plugin.parameters}
#         for param in self.parameters:
#             param.register_loader(loaders[param.name])

#     def _builder(self, wizard, prereqs):
#         dct = dict(prereqs)  # make a copy
#         dct.update({param.name: param(wizard) for param in self.parameters})
#         result = self.compiler_plugin(**dct)
#         return result

#     def __call__(self, wizard):
#         if self.intro is not None:
#             wizard.say(self.intro)

#         if self.prerequisite is not None:
#             prereqs = self.prerequisite(wizard)
#         else:
#             prereqs = {}

#         result = self._builder(wizard, prereqs)

#         return result

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


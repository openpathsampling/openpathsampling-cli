NO_PARAMETER_LOADED = object()

from .helper import Helper


class WrapCompilerWizardPlugin:
    def __init__(self, name, category, parameters, compiler_plugin,
                 prerequisite=None, intro=None, description=None):
        self.name = name
        self.parameters = parameters
        self.compiler_plugin = compiler_plugin
        self.prerequisite = prerequisite
        self.intro = intro
        self.description = description
        loaders = {p.name: p.loader for p in self.compiler_plugin.parameters}
        for param in self.parameters:
            param.register_loader(loaders[param.name])

    def _builder(self, wizard, prereqs):
        dct = dict(prereqs)  # make a copy
        dct.update({param.name: param(wizard) for param in self.parameters})
        result = self.compiler_plugin(**dct)
        return result

    def __call__(self, wizard):
        if self.intro is not None:
            wizard.say(self.intro)

        if self.prerequisite is not None:
            prereqs = self.prerequisite(wizard)
        else:
            prereqs = {}

        result = self._builder(wizard, prereqs)

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


class WrapCategory:
    def __init__(self, name, ask, helper=None, intro=None):
        self.name = name
        if isinstance(intro, str):
            intro = [intro]
        self.intro = intro
        self.ask = ask
        if helper is None:
            helper = Helper(CategoryHelpFunc(self))
        if isinstance(helper, str):
            helper = Helper(CategoryHelpFunc(self, helper))

        self.helper = helper
        self.choices = {}

    def register_plugin(self, plugin):
        self.choices[plugin.name] = plugin

    def __call__(self, wizard):
        for line in self.intro:
            wizard.say(line)

        selected = wizard.ask_enumerate_dict(self.ask, self.choices,
                                             self.helper)
        obj = selected(wizard)
        return obj


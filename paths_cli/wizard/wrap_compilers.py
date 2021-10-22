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


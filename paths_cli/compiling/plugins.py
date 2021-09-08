from paths_cli.compiling.core import InstanceCompilerPlugin
from paths_cli.plugin_management import OPSPlugin

class CategoryPlugin(OPSPlugin):
    """
    Category plugins only need to be made for top-level
    """
    error_on_duplicate = False  # TODO: temporary
    def __init__(self, plugin_class, aliases=None, requires_ops=(1, 0),
                 requires_cli=(0,4)):
        super().__init__(requires_ops, requires_cli)
        self.plugin_class = plugin_class
        if aliases is None:
            aliases = []
        self.aliases = aliases

    @property
    def name(self):
        return self.plugin_class.compiler_name

    def __repr__(self):
        return (f"CompilerPlugin({self.plugin_class.__name__}, "
                f"{self.aliases})")


class EngineCompilerPlugin(InstanceCompilerPlugin):
    compiler_name = 'engine'

class CVCompilerPlugin(InstanceCompilerPlugin):
    compiler_name = 'cv'

class VolumeCompilerPlugin(InstanceCompilerPlugin):
    compiler_name = 'volume'

class NetworkCompilerPlugin(InstanceCompilerPlugin):
    compiler_name = 'network'

class SchemeCompilerPlugin(InstanceCompilerPlugin):
    compiler_name = 'scheme'

class StrategyCompilerPlugin(InstanceCompilerPlugin):
    compiler_name = 'strategy'

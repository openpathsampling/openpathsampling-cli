from paths_cli.compiling.core import InstanceBuilder
from paths_cli.plugin_management import OPSPlugin

class CompilerPlugin(OPSPlugin):
    """
    Compiler plugins only need to be made for top-level
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


class EngineCompilerPlugin(InstanceBuilder):
    compiler_name = 'engine'

class CVCompilerPlugin(InstanceBuilder):
    compiler_name = 'cv'

class VolumeCompilerPlugin(InstanceBuilder):
    compiler_name = 'volume'

class NetworkCompilerPlugin(InstanceBuilder):
    compiler_name = 'network'

class SchemeCompilerPlugin(InstanceBuilder):
    compiler_name = 'scheme'

class StrategyCompilerPlugin(InstanceBuilder):
    compiler_name = 'strategy'

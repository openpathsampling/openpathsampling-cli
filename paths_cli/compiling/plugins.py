from paths_cli.compiling.core import InstanceCompilerPlugin
from paths_cli.plugin_management import OPSPlugin


class CategoryPlugin(OPSPlugin):
    """
    Category plugins only need to be made for top-level
    """
    def __init__(self, plugin_class, aliases=None, requires_ops=(1, 0),
                 requires_cli=(0, 3)):
        super().__init__(requires_ops, requires_cli)
        self.plugin_class = plugin_class
        if aliases is None:
            aliases = []
        self.aliases = aliases

    @property
    def name(self):
        return self.plugin_class.category

    def __repr__(self):
        return (f"CompilerPlugin({self.plugin_class.__name__}, "
                f"{self.aliases})")


class EngineCompilerPlugin(InstanceCompilerPlugin):
    category = 'engine'


class CVCompilerPlugin(InstanceCompilerPlugin):
    category = 'cv'


class VolumeCompilerPlugin(InstanceCompilerPlugin):
    category = 'volume'


class NetworkCompilerPlugin(InstanceCompilerPlugin):
    category = 'network'


class SchemeCompilerPlugin(InstanceCompilerPlugin):
    category = 'scheme'


class StrategyCompilerPlugin(InstanceCompilerPlugin):
    category = 'strategy'


class ShootingPointSelectorPlugin(InstanceCompilerPlugin):
    category = 'shooting-point-selector'


class InterfaceSetPlugin(InstanceCompilerPlugin):
    category = 'interface-set'

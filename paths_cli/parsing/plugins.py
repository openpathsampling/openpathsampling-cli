from paths_cli.parsing.core import InstanceBuilder
from paths_cli.plugin_management import OPSPlugin

class ParserPlugin(OPSPlugin):
    """
    Parser plugins only need to be made for top-level
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
        return self.plugin_class.parser_name


class EngineParserPlugin(InstanceBuilder):
    parser_name = 'engine'

class CVParserPlugin(InstanceBuilder):
    parser_name = 'cv'

class VolumeParserPlugin(InstanceBuilder):
    parser_name = 'volume'

class NetworkParserPlugin(InstanceBuilder):
    parser_name = 'network'

class SchemeParserPlugin(InstanceBuilder):
    parser_name =  'scheme'

class StrategyParserPlugin(InstanceBuilder):
    parser_name = 'strategy'

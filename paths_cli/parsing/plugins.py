from paths_cli.parsing.core import InstanceBuilder


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

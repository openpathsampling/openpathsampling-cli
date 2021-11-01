import os
from paths_cli.compiling.errors import InputError
from paths_cli.compiling.root_compiler import compiler_for


def get_topology_from_engine(dct):
    """If given the name of an engine, use that engine's topology"""
    engine_compiler = compiler_for('engine')
    if dct in engine_compiler.named_objs:
        engine = engine_compiler.named_objs[dct]
        return getattr(engine, 'topology', None)
    return None


def get_topology_from_file(dct):
    """If given the name of a file, use that to create the topology"""
    if os.path.exists(dct):
        import mdtraj as md
        import openpathsampling as paths
        trj = md.load(dct)
        return paths.engines.MDTrajTopology(trj.topology)
    return None


class MultiStrategyBuilder:
    # move to core
    def __init__(self, strategies, label, description=None, json_type=None):
        self.strategies = strategies
        self.label = label
        self.description = description
        self.json_type = json_type

    def __call__(self, dct):
        for strategy in self.strategies:
            result = strategy(dct)
            if result is not None:
                return result

        # only get here if we failed
        raise InputError.invalid_input(dct, self.label)


build_topology = MultiStrategyBuilder(
    [get_topology_from_file, get_topology_from_engine],
    label='topology',
    description="topology from file or engine name",
    json_type='string'
)

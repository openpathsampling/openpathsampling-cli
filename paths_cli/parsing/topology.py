import os
from .errors import InputError

def get_topology_from_engine(dct, named_objs):
    """If given the name of an engine, use that engine's topology"""
    if dct in named_objs:
        engine = named_objs[dct]
        try:
            return engine.topology
        except AttributeError:
            pass

def get_topology_from_file(dct, named_objs):
    """If given the name of a file, use that to create the topology"""
    if os.path.exists(dct):
        import mdtraj as md
        import openpathsampling as paths
        trj = md.load(dct)
        return paths.engines.openmm.topology.MDTrajTopology(trj.topology)


class MultiStrategyBuilder:
    # move to core
    def __init__(self, strategies, label):
        self.strategies = strategies
        self.label = label

    def __call__(self, dct, named_objs):
        for strategy in self.strategies:
            result = strategy(dct, named_objs)
            if result is not None:
                return result

        # only get here if we failed
        raise InputError.invalid_input(dct, self.label)

build_topology = MultiStrategyBuilder([get_topology_from_file,
                                       get_topology_from_engine],
                                      label='topology')

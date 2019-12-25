import pytest
import tempfile
import os

import openpathsampling as paths
from openpathsampling.tests.test_helpers import make_1d_traj

from paths_cli.parameters import *


class ParameterTest(object):
    def test_parameter(self):
        # this is just a smoke test to contrast with the ValueError case
        opt = self.Class("-f", "--foo", help="help")

    def test_option_with_requires(self):
        with pytest.raises(ValueError):
            opt = self.Class("-f", "--foo", help="help", required=True)

class TestOption(ParameterTest):
    Class = Option

class TestArgument(ParameterTest):
    Class = Argument

# NOTE: all the classes defined in this are actually tested using the
# instances -- we still get full coverage, and honestly, do a better job of
# testing

class ParamInstanceTest(object):
    def setup(self):
        pes = paths.engines.toy.Gaussian(1, [1.0, 1.0], [0.0, 0.0])
        integ = paths.engines.toy.LangevinBAOABIntegrator(0.01, 0.1, 2.5)
        topology = paths.engines.toy.Topology(n_spatial=2, n_atoms=1,
                                              masses=[1.0], pes=pes)
        self.engine = paths.engines.toy.Engine(
            options={'n_frames_max': 1000, 'n_steps_per_frame': 10,
                     'integ': integ},
            topology=topology
        ).named("engine")
        self.other_engine = paths.engines.toy.Engine(
            options={'n_frames_max': 5000, 'n_steps_per_frame': 1,
                     'integ': integ},
            topology=topology
        )
        self.cv = paths.FunctionCV("x", lambda x: x.xyz[0][0])
        self.state_A = paths.CVDefinedVolume(
            self.cv, float("-inf"), 0
        ).named("A")
        self.state_B = paths.CVDefinedVolume(
            self.cv, 10, float("inf")
        ).named("B")
        network = paths.TPSNetwork(self.state_A, self.state_B)
        self.scheme = paths.OneWayShootingMoveScheme(
            network,
            paths.UniformSelector(),
            self.engine
        ).named("scheme")
        self.other_scheme = paths.OneWayShootingMoveScheme(
            network,
            paths.UniformSelector(),
            self.other_engine
        )
        self.tempdir = tempfile.mkdtemp()

    def _filename(self, getter):
        return os.path.join(self.tempdir, getter + ".nc")

    def create_file(self, getter):
        filename = self._filename(getter)
        if getter == "named":
            self.other_scheme = self.other_scheme.named("other")
            self.other_engine = self.other_engine.named("other")

        storage = paths.Storage(filename, 'w')
        storage.save(self.engine)
        storage.save(self.cv)
        storage.save(self.state_A)
        storage.save(self.state_B)
        storage.save(self.scheme)

        if getter != "only":
            storage.save(self.other_scheme)
            storage.save(self.other_engine)

        storage.close()
        return filename

    def _getter_test(self, getter):
        test_file = self.create_file(getter)
        storage = paths.Storage(self._filename(getter), mode='r')
        get_arg = self.get_arg[getter]
        obj = self.PARAMETER.get(storage, get_arg)
        assert obj.__uuid__ == self.obj.__uuid__
        assert obj == self.obj

    def teardown(self):
        for temp_f in os.listdir(self.tempdir):
            os.remove(os.path.join(self.tempdir, temp_f))
        os.rmdir(self.tempdir)


class TestENGINE(ParamInstanceTest):
    PARAMETER = ENGINE
    def setup(self):
        super(TestENGINE, self).setup()
        self.get_arg = {'name': 'engine', 'number': 0, 'only': None,
                        'only-named': None}
        self.obj = self.engine

    @pytest.mark.parametrize("getter", ['name', 'number', 'only',
                                        'only-named'])
    def test_get(self, getter):
        self._getter_test(getter)


class TestSCHEME(ParamInstanceTest):
    PARAMETER = SCHEME
    def setup(self):
        super(TestSCHEME, self).setup()
        self.get_arg = {'name': 'scheme', 'number': 0, 'only': None,
                        'only-named': None}
        self.obj = self.scheme

    @pytest.mark.parametrize("getter", ['name', 'number', 'only',
                                        'only-named'])
    def test_get(self, getter):
        self._getter_test(getter)


class TestINIT_TRAJ(ParamInstanceTest):
    PARAMETER = INIT_TRAJ
    def setup(self):
        super(TestINIT_TRAJ, self).setup()
        self.traj = make_1d_traj([-0.1, 1.0, 4.4, 7.7, 10.01])
        ensemble = self.scheme.network.sampling_ensembles[0]
        self.sample_set = paths.SampleSet([
            paths.Sample(trajectory=self.traj,
                         replica=0,
                         ensemble=ensemble)
        ])
        self.other_traj = make_1d_traj([-1.0, 1.0, 100.0])
        self.other_sample_set = paths.SampleSet([
            paths.Sample(trajectory=self.other_traj,
                         replica=0,
                         ensemble=ensemble)
        ])

    @staticmethod
    def _parse_getter(getter):
        split_up = getter.split('-')
        get_type = split_up[-1]
        getter_style = "-".join(split_up[:-1])
        return get_type, getter_style

    def create_file(self, getter):
        filename = self._filename(getter)
        storage = paths.Storage(filename, 'w')
        storage.save(self.traj)
        storage.save(self.other_traj)
        get_type, getter_style = self._parse_getter(getter)
        main, other = {
            'traj': (self.traj, self.other_traj),
            'sset': (self.sample_set, self.other_sample_set)
        }[get_type]
        if get_type == 'sset':
            storage.save(self.sample_set)
            storage.save(self.other_sample_set)

        tag, other_tag = {
            'name': ('traj', None),
            'number': (None, None),
            'tag-final': ('final_conditions', 'initial_conditions'),
            'tag-initial': ('initial_conditions', None)
        }[getter_style]
        if tag:
            storage.tags[tag] = main

        if other_tag:
            storage.tags[other_tag] = other
        storage.close()
        return filename

    @pytest.mark.parametrize("getter", [
        'name-traj', 'number-traj', 'tag-final-traj', 'tag-initial-traj',
        'name-sset', 'number-sset', 'tag-final-sset', 'tag-initial-sset'
    ])
    def test_get(self, getter):
        filename = self.create_file(getter)
        storage = paths.Storage(filename, mode='r')
        get_type, getter_style = self._parse_getter(getter)
        expected = {
            'sset': self.sample_set,
            'traj': self.traj
        }[get_type]
        get_arg = {
            'name': 'traj',
            'number': 0,
            'tag-final': 'final_conditions',
            'tag-initial': 'initial_conditions'
        }[getter_style]
        obj = self.PARAMETER.get(storage, get_arg)

        pytest.skip()
        pass

    def test_get_file(self):
        pytest.skip()


class TestCVS(ParamInstanceTest):
    PARAMETER = CVS
    def setup(self):
        super(TestCVS, self).setup()
        self.get_arg = {'name': "x", 'number': 0}
        self.obj = self.cv

    @pytest.mark.parametrize("getter", ['name', 'number'])
    def test_get(self, getter):
        self._getter_test(getter)


class TestSTATES(ParamInstanceTest):
    PARAMETER = STATES
    def setup(self):
        super(TestSTATES, self).setup()
        self.get_arg = {'name': "A", 'number': 0}
        self.obj = self.state_A

    @pytest.mark.parametrize("getter", ['name', 'number'])
    def test_get(self, getter):
        self._getter_test(getter)

    @pytest.mark.parametrize("getter", ['name', 'number'])
    def test_get_other(self, getter):
        self.get_arg = {'name': 'B', 'number': 1}
        self.obj = self.state_B
        self._getter_test(getter)

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
        self.network = paths.TPSNetwork(self.state_A,
                                        self.state_B).named('network')
        self.scheme = paths.OneWayShootingMoveScheme(
            self.network,
            paths.UniformSelector(),
            self.engine
        ).named("scheme")
        self.other_scheme = paths.OneWayShootingMoveScheme(
            self.network,
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
                        'only-named': None, 'bad-name': 'foo'}
        self.obj = self.scheme

    @pytest.mark.parametrize("getter", ['name', 'number', 'only',
                                        'only-named'])
    def test_get(self, getter):
        self._getter_test(getter)

    def test_bad_get(self):
        # NOTE: This is where we test the failure of get; don't need to do
        # it in every parameter
        with pytest.raises(RuntimeError):
            obj = self._getter_test('bad-name')



class TestINIT_CONDS(ParamInstanceTest):
    PARAMETER = INIT_CONDS
    def setup(self):
        super(TestINIT_CONDS, self).setup()
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
        assert obj == expected

    @pytest.mark.parametrize("num_in_file", [1, 2, 3, 4])
    def test_get_none(self, num_in_file):
        stored_things = [
            self.traj, self.sample_set, self.other_sample_set,
            self.other_sample_set
        ]
        to_store = stored_things[:num_in_file]
        filename = self._filename("init_conds_" + str(num_in_file) + ".nc")
        storage = paths.Storage(filename, mode='w')
        for item in to_store:
            storage.save(item)

        if num_in_file == 3:
            storage.tags['initial_conditions'] = self.other_sample_set
        elif num_in_file == 4:
            storage.tags['final_conditions'] = self.other_sample_set
            storage.tags['initial_conditions'] = self.sample_set

        storage.close()

        st = paths.Storage(filename, mode='r')
        obj = INIT_CONDS.get(st, None)
        assert obj == stored_things[num_in_file - 1]

class TestINIT_SNAP(ParamInstanceTest):
    PARAMETER = INIT_SNAP
    def setup(self):
        super(TestINIT_SNAP, self).setup()
        traj = make_1d_traj([1.0, 2.0])
        self.other_snap = traj[0]
        self.init_snap = traj[1]

    def create_file(self, getter):
        filename = self._filename(getter)
        storage = paths.Storage(filename, 'w')
        storage.save(self.other_snap)
        if getter != 'none-num':
            storage.save(self.init_snap)
            storage.tags['initial_snapshot'] = self.init_snap
        storage.close()
        return filename

    @pytest.mark.parametrize('getter', ['none-num', 'tag', 'number',
                                        'none-tag'])
    def test_get(self, getter):
        # get by number is 2 because of snapshot duplication in storage
        get_arg = {'none-num': None,
                   'none-tag': None,
                   'tag': 'initial_snapshot',
                   'number': 2}[getter]
        expected = {'none-num': self.other_snap,
                    'none-tag': self.init_snap,
                    'tag': self.init_snap,
                    'number': self.init_snap}[getter]
        filename = self.create_file(getter)
        storage = paths.Storage(filename, mode='r')

        obj = self.PARAMETER.get(storage, get_arg)
        assert obj == expected


class MultiParamInstanceTest(ParamInstanceTest):
    def _getter_test(self, getter):
        test_file = self.create_file(getter)
        storage = paths.Storage(self._filename(getter), mode='r')
        get_arg = self.get_arg[getter]
        obj_list = self.PARAMETER.get(storage, get_arg)
        for obj in obj_list:
            assert obj.__uuid__ == self.obj.__uuid__
            assert obj == self.obj


class TestCVS(MultiParamInstanceTest):
    PARAMETER = CVS
    def setup(self):
        super(TestCVS, self).setup()
        self.get_arg = {'name': ["x"], 'number': [0]}
        self.obj = self.cv

    @pytest.mark.parametrize("getter", ['name', 'number'])
    def test_get(self, getter):
        self._getter_test(getter)


class TestSTATES(MultiParamInstanceTest):
    PARAMETER = STATES
    def setup(self):
        super(TestSTATES, self).setup()
        self.get_arg = {'name': ["A"], 'number': [0]}
        self.obj = self.state_A

    @pytest.mark.parametrize("getter", ['name', 'number'])
    def test_get(self, getter):
        self._getter_test(getter)

    @pytest.mark.parametrize("getter", ['name', 'number'])
    def test_get_other(self, getter):
        self.get_arg = {'name': ['B'], 'number': [1]}
        self.obj = self.state_B
        self._getter_test(getter)


class MULTITest(MultiParamInstanceTest):
    # Abstract base class for tests of MULTI_* parameters
    # These parameters require name or number input, otherwise error
    @pytest.mark.parametrize("getter", ['name', 'number'])
    def test_get(self, getter):
        self._getter_test(getter)

    def test_get_none(self):
        filename = self.create_file("none")
        storage = paths.Storage(filename, mode='r')
        with pytest.raises(TypeError):
            # TypeError: 'NoneType' object is not iterable
            self.PARAMETER.get(storage, None)


class TestMULTI_VOLUME(TestSTATES, MULTITest):
    PARAMETER = MULTI_VOLUME
    # MULTI_VOLUME is basically the same as STATES, with different option
    # parameters


class TestMULTI_ENGINE(MULTITest):
    PARAMETER = MULTI_ENGINE
    def setup(self):
        super(TestMULTI_ENGINE, self).setup()
        self.get_arg = {'name': ["engine"], 'number': [0]}
        self.obj = self.engine


class TestMulti_NETWORK(MULTITest):
    PARAMETER = MULTI_NETWORK
    def setup(self):
        super(TestMulti_NETWORK, self).setup()
        self.get_arg = {'name': ['network'], 'number': [0]}
        self.obj = self.network


class TestMULTI_SCHEME(MULTITest):
    PARAMETER = MULTI_SCHEME
    def setup(self):
        super(TestMULTI_SCHEME, self).setup()
        self.get_arg = {'name': ['scheme'], 'number': [0]}
        self.obj = self.scheme


class TestMULTI_TAG(MULTITest):
    PARAMETER = MULTI_TAG
    def setup(self):
        super(TestMULTI_TAG, self).setup()
        self.obj = make_1d_traj([1.0, 2.0, 3.0])
        self.get_arg = {'name': ['traj']}

    def create_file(self, getter):
        filename = self._filename(getter)
        storage = paths.Storage(filename, 'w')
        storage.tag['traj'] = self.obj
        storage.close()
        return filename

    @pytest.mark.parametrize("getter", ['name'])
    def test_get(self, getter):
        self._getter_test(getter)


def test_OUTPUT_FILE():
    tempdir = tempfile.mkdtemp()
    filename = os.path.join(tempdir, "test_output_file.nc")
    assert not os.path.exists(filename)
    storage = OUTPUT_FILE.get(filename)
    assert os.path.exists(filename)
    os.remove(filename)
    os.rmdir(tempdir)

def test_APPEND_FILE():
    tempdir = tempfile.mkdtemp()
    filename = os.path.join(tempdir, "test_append_file.nc")
    assert not os.path.exists(filename)
    storage = APPEND_FILE.get(filename)
    print(storage)
    assert os.path.exists(filename)
    traj = make_1d_traj([0.0, 1.0])
    storage.tags['first_save'] = traj[0]
    storage.close()
    storage = APPEND_FILE.get(filename)
    assert storage.tags['first_save'] == traj[0]
    storage.tags['second_save'] = traj[1]
    storage.close()
    storage = APPEND_FILE.get(filename)
    assert len(storage.tags) == 2
    storage.close()
    os.remove(filename)
    os.rmdir(tempdir)

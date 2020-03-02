import os
import tempfile
from unittest.mock import MagicMock, patch
import pytest


import openpathsampling as paths
from openpathsampling.tests.test_helpers import make_1d_traj

from paths_cli.file_copying import *

class Test_PRECOMPUTE_CVS(object):
    def setup(self):
        self.tmpdir = tempfile.mkdtemp()
        self.storage_filename = os.path.join(self.tmpdir, "test.nc")
        self.storage = paths.Storage(self.storage_filename, mode='w')
        snap = make_1d_traj([1])[0]
        self.storage.save(snap)
        self.cv_x = paths.CoordinateFunctionCV("x", lambda s: s.xyz[0][0])
        self.cv_y = paths.CoordinateFunctionCV("y", lambda s: s.xyz[0][1])
        self.storage.save([self.cv_x, self.cv_y])

    def teardown(self):
        self.storage.close()

        for filename in os.listdir(self.tmpdir):
            os.remove(os.path.join(self.tmpdir, filename))
        os.rmdir(self.tmpdir)

    @pytest.mark.parametrize('getter', ['x', None, '--'])
    def test_get(self, getter):
        expected = {'x': [self.cv_x],
                    None: [self.cv_x, self.cv_y],
                    '--': []}[getter]
        getter = [] if getter is None else [getter]  # CLI gives a list
        cvs = PRECOMPUTE_CVS.get(self.storage, getter)
        assert len(cvs) == len(expected)
        assert set(cvs) == set(expected)


@pytest.mark.parametrize('blocksize', [2, 3, 5, 10, 12])
def test_make_blocks(blocksize):
    expected_lengths = {2: [2, 2, 2, 2, 2],
                        3: [3, 3, 3, 1],
                        5: [5, 5],
                        10: [10],
                        12: [10]}[blocksize]
    ll = list(range(10))
    blocks = make_blocks(ll, blocksize)
    assert [len(block) for block in blocks] == expected_lengths
    assert sum(blocks, []) == ll


class TestPrecompute(object):
    def setup(self):
        class RunOnceFunction(object):
            def __init__(self):
                self.previously_seen = set([])

            def __call__(self, snap):
                if snap in self.previously_seen:
                    raise AssertionError("Second CV eval for " + str(snap))
                self.previously_seen.update({snap})
                return snap.xyz[0][0]

        self.cv = paths.FunctionCV("test", RunOnceFunction())
        traj = paths.tests.test_helpers.make_1d_traj([2, 1])
        self.snap = traj[0]
        self.other_snap = traj[1]

    def test_precompute_cvs(self):
        precompute_cvs([self.cv], [self.snap])
        assert self.cv.f.previously_seen == {self.snap}
        recalced = self.cv(self.snap)  # AssertionError if func called
        assert recalced == 2
        assert self.cv.diskcache_enabled is True

    def test_precompute_cvs_and_inputs(self):
        pytest.skip()


def test_rewrite_file():
    pytest.skip()

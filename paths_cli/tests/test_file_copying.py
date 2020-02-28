import os

import pytest

from paths_cli.file_copying import *

class Test_PRECOMPUTE_CVS(object):
    pass


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
    def test_precompute_cvs(self):
        pytest.skip()

    def test_precompute_cvs_and_inputs(self):
        pytest.skip()


def test_rewrite_file():
    pytest.skip()

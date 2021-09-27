import pytest
import numpy.testing as npt
import numpy as np
import math
from paths_cli.compiling.errors import InputError

from paths_cli.compiling.tools import *

@pytest.mark.parametrize('expr,expected', [
    ('1+1', 2),
    ('np.pi / 2', np.pi / 2),
    ('math.cos(1.5)', math.cos(1.5)),
])
def test_custom_eval(expr, expected):
    npt.assert_allclose(custom_eval(expr), expected)

def test_custom_eval_int():
    assert custom_eval_int('5') == 5

@pytest.mark.parametrize('inp', [0, -1])
def test_custom_eval_int_strict_pos_error(inp):
    with pytest.raises(InputError):
        custom_eval_int_strict_pos(inp)

def test_mdtraj_parse_atomlist_bad_input():
    with pytest.raises(TypeError, match="not integers"):
        mdtraj_parse_atomlist("['a', 'b']", n_atoms=2)

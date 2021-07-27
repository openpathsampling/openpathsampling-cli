import pytest
import numpy.testing as npt
import numpy as np
import math

from paths_cli.parsing.tools import *

@pytest.mark.parametrize('expr,expected', [
    ('1+1', 2),
    ('np.pi / 2', np.pi / 2),
    ('math.cos(1.5)', math.cos(1.5)),
])
def test_custom_eval(expr, expected):
    npt.assert_allclose(custom_eval(expr), expected)

def test_mdtraj_parse_atomlist_bad_input():
    with pytest.raises(TypeError, match="not integers"):
        mdtraj_parse_atomlist("['a', 'b']", n_atoms=2)

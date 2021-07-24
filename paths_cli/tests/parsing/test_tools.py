import pytest
import numpy.testing as npt

from paths_cli.parsing.tools import *

@pytest.mark.parametrize('expr,expected', [
    ('1+1', 2)
])
def test_custom_eval(expr, expected):
    npt.assert_allclose(custom_eval(expr), expected)

def test_mdtraj_parse_atomlist_bad_input():
    with pytest.raises(TypeError, match="not integers"):
        mdtraj_parse_atomlist("['a', 'b']", n_atoms=2)

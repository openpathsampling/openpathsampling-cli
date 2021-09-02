import pytest
from unittest import mock

from paths_cli.tests.wizard.mock_wizard import mock_wizard
from paths_cli.tests.utils import assert_url

from paths_cli.wizard.openmm import (
    _load_openmm_xml, _load_topology, openmm, OPENMM_SERIALIZATION_URL
)

try:
    import openmm as mm
except ImportError:
    try:
        from simtk import openmm as mm
    except ImportError:
        HAS_OPENMM = False
    else:
        HAS_OPENMM = True  # -no-cov-
else:
    HAS_OPENMM = True

def test_helper_url():
    assert_url(OPENMM_SERIALIZATION_URL)

@pytest.mark.parametrize('obj_type', ['system', 'integrator', 'foo'])
def test_load_openmm_xml(ad_openmm, obj_type):
    if not HAS_OPENMM:
        pytest.skip()
    # mm = pytest.importorskip("simtk.openmm")
    filename = f"{obj_type}.xml"
    inputs = [filename]
    expected_count = 1
    if obj_type == 'foo':
        inputs.append('integrator.xml')
        expected_count = 2

    wizard = mock_wizard(inputs)
    superclass = {'integrator': mm.CustomIntegrator,
                  'system': mm.System,
                  'foo': mm.CustomIntegrator}[obj_type]
    with ad_openmm.as_cwd():
        obj = _load_openmm_xml(wizard, obj_type)
        assert isinstance(obj, superclass)

    assert wizard.console.input_call_count == expected_count

@pytest.mark.parametrize('setup', ['normal', 'bad_filetype', 'no_file'])
def test_load_topology(ad_openmm, setup):
    import openpathsampling as paths
    inputs = {'normal': [],
              'bad_filetype': ['foo.bar'],
              'no_file': ['foo.pdb']}[setup]
    expected_text = {'normal': "PDB file",
                     'bad_filetype': 'trr',
                     'no_file': 'No such file'}[setup]
    inputs += ['ad.pdb']
    wizard = mock_wizard(inputs)
    with ad_openmm.as_cwd():
        top = _load_topology(wizard)

    assert isinstance(top, paths.engines.MDTrajTopology)
    assert wizard.console.input_call_count == len(inputs)
    assert expected_text in wizard.console.log_text

def test_openmm(ad_openmm):
    inputs = ['system.xml', 'integrator.xml', 'ad.pdb', '10', '10000']
    wizard = mock_wizard(inputs)
    with ad_openmm.as_cwd():
        engine = openmm(wizard)
    assert engine.n_frames_max == 10000
    assert engine.n_steps_per_frame == 10

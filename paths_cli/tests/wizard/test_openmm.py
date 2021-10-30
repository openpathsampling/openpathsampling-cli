import pytest
from unittest import mock

from paths_cli.tests.wizard.mock_wizard import mock_wizard
from paths_cli.tests.utils import assert_url

from paths_cli.wizard.openmm import (
    OPENMM_PLUGIN, OPENMM_SERIALIZATION_URL
)

from paths_cli.compat.openmm import mm, HAS_OPENMM

def test_helper_url():
    assert_url(OPENMM_SERIALIZATION_URL)

def test_openmm(ad_openmm):
    inputs = ['ad.pdb', 'integrator.xml', 'system.xml', '10', '10000']
    wizard = mock_wizard(inputs)
    with ad_openmm.as_cwd():
        engine = OPENMM_PLUGIN(wizard)
    assert engine.n_frames_max == 10000
    assert engine.n_steps_per_frame == 10

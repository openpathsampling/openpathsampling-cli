import pytest
from unittest import mock

from paths_cli.tests.wizard.mock_wizard import mock_wizard

from paths_cli.wizard.two_state_tps import two_state_tps

def mock_tps_scheme(wizard, network):
    wizard.say(str(network.__class__))
    return "this would be a scheme"

@mock.patch('paths_cli.wizard.two_state_tps.tps_scheme',
            new=mock_tps_scheme)
def test_two_state_tps(tps_network):
    wizard = mock_wizard([])
    state_A = tps_network.initial_states[0]
    state_B = tps_network.final_states[0]
    with mock.patch('paths_cli.wizard.two_state_tps.volumes',
                    new=mock.Mock(side_effect=[state_A, state_B])):
        scheme = two_state_tps(wizard)
    assert scheme == "this would be a scheme"
    assert "network.TPSNetwork" in wizard.console.log_text




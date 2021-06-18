import pytest
from unittest import mock

from functools import partial

import openpathsampling as paths
from openpathsampling import strategies

from paths_cli.tests.wizard.mock_wizard import mock_wizard

from paths_cli.wizard.tps import tps_scheme

@pytest.mark.parametrize('as_scheme', [False, True])
def test_tps_scheme(tps_network, toy_engine, as_scheme):
    wizard = mock_wizard([])
    wizard.networks = {tps_network.name: tps_network}
    if as_scheme:
        strategy = partial(paths.SpringShootingMoveScheme,
                           k_spring=0.01,
                           delta_max=10,
                           engine=toy_engine)
    else:
        strategy = strategies.OneWayShootingStrategy(
            selector=paths.UniformSelector(),
            engine=toy_engine
        )
    with mock.patch('paths_cli.wizard.tps.shooting',
                    new=mock.Mock(return_value=strategy)):
        scheme = tps_scheme(wizard)

    assert isinstance(scheme, paths.MoveScheme)
    if as_scheme:
        assert isinstance(scheme, paths.SpringShootingMoveScheme)

import pytest
from unittest import mock
from functools import partial

from paths_cli.tests.wizard.mock_wizard import mock_wizard

from paths_cli.wizard.shooting import (
    # selectors
    uniform_selector, gaussian_selector, _get_selector, SHOOTING_SELECTORS,
    # shooting algorithms
    one_way_shooting, spring_shooting,
    # main func
    shooting, SHOOTING_TYPES
)

import openpathsampling as paths
from openpathsampling.experimental.storage.collective_variables import \
        CoordinateFunctionCV

def test_uniform_selector():
    wizard = mock_wizard([])
    sel = uniform_selector(wizard)
    assert isinstance(sel, paths.UniformSelector)
    assert wizard.console.input_call_count == 0

def test_gaussian_selector():
    wizard = mock_wizard(['x', '1.0', '0.5'])
    cv = CoordinateFunctionCV(lambda s: s.xyz[0][0]).named('x')
    wizard.cvs[cv.name] = cv
    sel = gaussian_selector(wizard)
    assert isinstance(sel, paths.GaussianBiasSelector)
    assert sel.alpha == 2.0
    assert sel.l_0 == 1.0

def test_get_selector():
    wizard = mock_wizard(['Uniform random'])
    sel = _get_selector(wizard)
    assert isinstance(sel, paths.UniformSelector)

def test_one_way_shooting(toy_engine):
    wizard = mock_wizard(['Uniform random'])
    wizard.engines[toy_engine.name] = toy_engine
    strategy = one_way_shooting(wizard)
    assert isinstance(strategy, paths.strategies.OneWayShootingStrategy)
    assert isinstance(strategy.selector, paths.UniformSelector)
    assert strategy.engine == toy_engine

def test_spring_shooting(toy_engine):
    wizard = mock_wizard(['10', '0.25'])
    wizard.engines[toy_engine.name] = toy_engine
    strategy = spring_shooting(wizard)
    assert isinstance(strategy, partial)
    assert strategy.func == paths.SpringShootingMoveScheme
    assert strategy.keywords['delta_max'] == 10
    assert strategy.keywords['k_spring'] == 0.25
    assert strategy.keywords['engine'] == toy_engine

@pytest.mark.parametrize('shooting_types', [{}, None])
def test_shooting(toy_engine, shooting_types):
    key = 'One-way (stochastic) shooting'
    wizard = mock_wizard([key])
    wizard.engines[toy_engine.name] = toy_engine
    foo = mock.Mock(return_value='foo')
    if shooting_types == {}:
        shooting_types = {key: foo}
    with mock.patch.dict(SHOOTING_TYPES, {key: foo}):
        assert shooting(wizard, shooting_types=shooting_types) == 'foo'

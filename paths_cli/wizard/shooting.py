from functools import partial

from paths_cli.wizard.core import get_missing_object
from paths_cli.wizard.plugin_registration import get_category_wizard


engines = get_category_wizard('engine')


def uniform_selector(wizard):
    """Create a uniform selector (using the wizard)"""
    import openpathsampling as paths
    return paths.UniformSelector()


def gaussian_selector(wizard):
    """Create a Gaussian biased selector (using the wizard)"""
    import openpathsampling as paths
    cv_name = wizard.ask_enumerate("Which CV do you want the Gaussian to "
                                   "be based on?",
                                   options=wizard.cvs.keys())
    cv = wizard.cvs[cv_name]
    l_0 = wizard.ask_custom_eval(f"At what value of {cv.name} should the "
                                 "Gaussian be centered?")
    std = wizard.ask_custom_eval("What should be the standard deviation of "
                                 "the Gaussian?")
    alpha = 0.5 / (std**2)
    selector = paths.GaussianBiasSelector(cv, alpha=alpha, l_0=l_0)
    return selector

# def random_velocities(wizard):
    # pass

# def gaussian_momentum_shift(wizard):
    # pass

# def get_allowed_modifiers(engine):
    # allowed = []
    # randomize_attribs = ['randomize_velocities', 'apply_constraints']
    # if any(hasattr(engine, attr) for attr in randomize_attribs):
        # allowed.append('random_velocities')

    # if not engine.has_constraints():
        # allowed.append('velocity_changers')

    # return allowed


SHOOTING_SELECTORS = {
    'Uniform random': uniform_selector,
    'Gaussian bias': gaussian_selector,
}


def _get_selector(wizard, selectors=None):
    if selectors is None:
        selectors = SHOOTING_SELECTORS
    selector = None
    sel = wizard.ask_enumerate("How do you want to select shooting "
                               "points?", options=list(selectors.keys()))
    selector = selectors[sel](wizard)
    return selector


def one_way_shooting(wizard, selectors=None, engine=None):
    from openpathsampling import strategies
    if engine is None:
        engine = get_missing_object(wizard, wizard.engines, 'engine',
                                    engines)

    selector = _get_selector(wizard, selectors)
    strat = strategies.OneWayShootingStrategy(selector=selector,
                                              engine=engine)
    return strat

# def two_way_shooting(wizard, selectors=None, modifiers=None):
    # pass


def spring_shooting(wizard, engine=None):
    import openpathsampling as paths
    if engine is None:
        engine = get_missing_object(wizard, wizard.engines, 'engine',
                                    engines)

    delta_max = wizard.ask_custom_eval(
        "What is the maximum shift (delta_max) in frames?", type_=int
    )
    k_spring = wizard.ask_custom_eval("What is the spring constant k?",
                                      type_=float)
    strat = partial(paths.SpringShootingMoveScheme,
                    delta_max=delta_max,
                    k_spring=k_spring,
                    engine=engine)
    return strat


SHOOTING_TYPES = {
    'One-way (stochastic) shooting': one_way_shooting,
    # 'Two-way shooting': two_way_shooting,
    'Spring shooting': spring_shooting,
}


def shooting(wizard, shooting_types=None, engine=None):
    if shooting_types is None:
        shooting_types = SHOOTING_TYPES

    if engine is None:
        engine = get_missing_object(wizard, wizard.engines, 'engine',
                                    engines)

    # allowed_modifiers = get_allowed_modifiers(engine)
    # TWO_WAY = 'Two-way shooting'
    # if len(allowed_modifiers) == 0 and TWO_WAY in shooting_types:
    #     del shooting_types[TWO_WAY]
    # else:
    #     shooting_types[TWO_WAY] = partial(two_way_shooting,
    #                                       allowed_modifiers=allowed_modifiers)

    shooting_type = None
    if len(shooting_types) == 1:
        shooting_type = list(shooting_types.values())[0]
    else:
        type_name = wizard.ask_enumerate(
            "Select the type of shooting move.",
            options=list(shooting_types.keys())
        )
        shooting_type = shooting_types[type_name]

    shooting_strategy = shooting_type(wizard)
    return shooting_strategy

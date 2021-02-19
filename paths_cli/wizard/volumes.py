import operator
from paths_cli.wizard.core import interpret_req
from paths_cli.wizard.cvs import cvs

def _vol_intro(wizard, as_state):
    if as_state:
        req = wizard.requirements['states']
        if len(wizard.states) == 0:
            intro = ("Now let's define stable states for your system. "
                     f"You'll need to define {interpret_req(req)} of them.")
        else:
            intro = "Okay, let's define another stable state."
    else:
        intro = None
    return intro

def _binary_func_volume(wizard, op):
    wizard.say("Let's make the first constituent volume:")
    vol1 = volumes(wizard)
    wizard.say(f"The first volume is:\n{str(vol1)}")
    wizard.say("Let's make the second constituent volume:")
    vol2 = volumes(wizard)
    wizard.say(f"The second volume is:\n{str(vol2)}")
    vol = op(vol1, vol2)
    wizard.say(f"Created a volume:\n{str(vol)}")
    return vol

def intersection_volume(wizard):
    wizard.say("This volume will be the intersection of two other volumes. "
               "This means that it only allows phase space points that are "
               "in both of the constituent volumes.")
    return _binary_func_volume(wizard, operator.__and__)

def union_volume(wizard):
    wizard.say("This volume will be the union of two other volumes. "
               "This means that it allows phase space points that are in "
               "either of the constituent volumes.")
    return _binary_func_volume(wizard, operator.__or__)

def negated_volume(wizard):
    wizard.say("This volume will be everything not in the subvolume.")
    wizard.say("Let's make the subvolume.")
    subvol = volumes(wizard)
    vol = ~subvol
    wizard.say(f"Created a volume:\n{str(vol)}")
    return vol

def cv_defined_volume(wizard):
    import openpathsampling as paths
    wizard.say("A CV-defined volume allows an interval in a CV.")
    cv = wizard.obj_selector('cvs', "CV", cvs)
    period_min = period_max = lambda_min = lambda_max = None
    is_periodic = None
    while is_periodic is None:
        is_periodic_char = wizard.ask("Is this CV periodic?",
                                      options=["[Y]es", "[N]o"])
        is_periodic = {'y': True, 'n': False}[is_periodic_char]

    if is_periodic:
        while period_min is None:
            period_min = wizard.ask_custom_eval(
                "What is the lower bound of the period?"
            )
        while period_max is None:
            period_max = wizard.ask_custom_eval(
                "What is the upper bound of the period?"
            )

    volume_bound_str = ("What is the {bound} allowed value for "
                        f"'{cv.name}' in this volume?")

    while lambda_min is None:
        lambda_min = wizard.ask_custom_eval(
            volume_bound_str.format(bound="minimum")
        )

    while lambda_max is None:
        lambda_max = wizard.ask_custom_eval(
            volume_bound_str.format(bound="maximum")
        )

    if is_periodic:
        vol = paths.PeriodicCVDefinedVolume(
            cv, lambda_min=lambda_min, lambda_max=lambda_max,
            period_min=period_min, period_max=period_max
        )
    else:
        vol = paths.CVDefinedVolume(
            cv, lambda_min=lambda_min, lambda_max=lambda_max,
        )
    return vol


SUPPORTED_VOLUMES = {
    'CV-defined volume (allowed values of CV)': cv_defined_volume,
    'Intersection of two volumes (must be in both)': intersection_volume,
    'Union of two volumes (must be in at least one)': union_volume,
    'Complement of a volume (not in given volume)': negated_volume,
}

def volumes(wizard, as_state=False):
    intro = _vol_intro(wizard, as_state)
    if intro is not None:
        wizard.say(_vol_intro(wizard, as_state))

    wizard.say("You can describe this as either a range of values for some "
               "CV, or as some combination of other such volumes "
               "(i.e., intersection or union).")
    obj = "state" if as_state else "volume"
    vol = None
    while vol is None:
        vol_type = wizard.ask_enumerate(
            f"What describes this {obj}?",
            options=list(SUPPORTED_VOLUMES.keys())
        )
        vol = SUPPORTED_VOLUMES[vol_type](wizard)

    return vol


if __name__ == "__main__":
    from paths_cli.wizard.wizard import Wizard
    wiz = Wizard({'states': ('states', 1, '+')})
    volumes(wiz, as_state=True)


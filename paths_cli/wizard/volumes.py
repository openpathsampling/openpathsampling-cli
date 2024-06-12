import operator
from functools import partial
from paths_cli.wizard.parameters import ProxyParameter
from paths_cli.wizard.plugin_classes import (
    LoadFromOPS, WizardParameterObjectPlugin, WizardObjectPlugin,
    WrapCategory
)
from paths_cli.wizard.helper import EvalHelperFunc, Helper
from paths_cli.wizard.core import interpret_req
import paths_cli.compiling.volumes
from paths_cli.wizard import pause


def _binary_func_volume(wizard, context, op):
    wizard.say("Let's make the first constituent volume.")
    pause.long(wizard)
    new_context = volume_set_context(wizard, context, selected=None)
    new_context['part'] = 1
    vol1 = VOLUMES_PLUGIN(wizard, new_context)
    pause.section(wizard)
    wizard.say("Let's make the second constituent volume.")
    pause.long(wizard)
    new_context['part'] = 2
    vol2 = VOLUMES_PLUGIN(wizard, new_context)
    pause.section(wizard)
    wizard.say("Now we'll combine those two constituent volumes...")
    vol = op(vol1, vol2)
    return vol


_LAMBDA_HELP = ("This is the {minmax} boundary value for this volume. "
                "Note that periodic CVs will correctly wrap values "
                "outside the periodic bounds.")
_LAMBDA_STR = ("What is the {minmax} allowed value for "
               "'{{obj_dict[cv].name}}' in this volume?")


CV_DEFINED_VOLUME_PLUGIN = WizardParameterObjectPlugin.from_proxies(
    name="CV-defined volume (allowed values of CV)",
    category="volume",
    description="Create a volume based on an interval along a chosen CV",
    intro="A CV-defined volume defines an interval along a chosen CV",
    parameters=[
        ProxyParameter(
            name='cv',
            ask=None,  # use internal tricks
            helper="Select the CV to use to define the volume.",
        ),
        ProxyParameter(
            name="lambda_min",
            ask=_LAMBDA_STR.format(minmax="minimum"),
            helper=Helper(
                EvalHelperFunc(_LAMBDA_HELP.format(minmax="minimum"))
            ),
        ),
        ProxyParameter(
            name='lambda_max',
            ask=_LAMBDA_STR.format(minmax="maximum"),
            helper=Helper(
                EvalHelperFunc(_LAMBDA_HELP.format(minmax="maximum"))
            ),
        ),
    ],
    compiler_plugin=paths_cli.compiling.volumes.CV_VOLUME_PLUGIN,
)


INTERSECTION_VOLUME_PLUGIN = WizardObjectPlugin(
    name='Intersection of two volumes (must be in both)',
    category="volume",
    intro=("This volume will be the intersection of two other volumes. "
           "This means that it only allows phase space points that are "
           "in both of the constituent volumes."),
    builder=partial(_binary_func_volume, op=operator.__and__),
    description=("Create a volume that is the intersection of two existing "
                 "volumes -- that is, all points in this volume are in "
                 "both of the volumes that define it."),
)


UNION_VOLUME_PLUGIN = WizardObjectPlugin(
    name='Union of two volumes (must be in at least one)',
    category="volume",
    intro=("This volume will be the union of two other volumes. "
           "This means that it allows phase space points that are in "
           "either of the constituent volumes."),
    builder=partial(_binary_func_volume, op=operator.__or__),
    description=("Create a volume that is the union of two existing "
                 "volumes -- that is, any point in either of the volumes "
                 "that define this are also in this volume"),
)


NEGATED_VOLUME_PLUGIN = WizardObjectPlugin(
    name='Complement of a volume (not in given volume)',
    category='volume',
    intro=("This volume will be everything not in the input volume, which "
           "you will define now."),
    builder=lambda wizard, context: ~VOLUMES_PLUGIN(
        wizard, volume_set_context(wizard, context, None)
    ),
    description=("Create a volume that includes every that is NOT "
                 "in the existing volume."),
)


_FIRST_STATE = ("Now  let's define state states for your system. "
                "You'll need to define {n_states_string} of them.")
_ADDITIONAL_STATES = "Okay, let's define another stable state."
_VOL_DESC = ("You can describe this as either a range of values for some "
             "CV, or as some combination of other such volumes "
             "(i.e., intersection or union).")


def volume_intro(wizard, context):
    as_state = context.get('depth', 0) == 0
    n_states = len(wizard.states)
    n_states_string = interpret_req(wizard.requirements['state'])
    intro = []
    if as_state:
        if n_states == 0:
            intro += [_FIRST_STATE.format(n_states_string=n_states_string)]
        else:
            intro += [_ADDITIONAL_STATES]

    intro += [_VOL_DESC]
    return intro


def volume_set_context(wizard, context, selected):
    depth = context.get('depth', 0) + 1
    new_context = {
        'depth': depth,
    }
    return new_context


def volume_ask(wizard, context):
    as_state = context.get('depth', 0) == 0
    obj = {True: 'state', False: 'volume'}[as_state]
    return f"What describes this {obj}?"


VOLUME_FROM_FILE = LoadFromOPS('volume')

VOLUMES_PLUGIN = WrapCategory(
    name='volume',
    intro=volume_intro,
    ask=volume_ask,
    set_context=volume_set_context,
    helper=("This will define a (hyper)volume in phase space. States and "
            "interfaces in OPS are described by volumes. You can combine "
            "ranges along different CVs in any way you want to defined the "
            "volume.")
)

if __name__ == "__main__":  # no-cov
    from paths_cli.wizard.run_module import run_category
    run_category('volume', {'state': ('volumes', 1, 1)})

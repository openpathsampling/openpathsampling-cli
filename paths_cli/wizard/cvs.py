from paths_cli.wizard.engines import engines
from paths_cli.compiling.tools import custom_eval, mdtraj_parse_atomlist
from paths_cli.wizard.load_from_ops import load_from_ops, LoadFromOPS
from paths_cli.wizard.load_from_ops import LABEL as _load_label
from paths_cli.wizard.core import get_object
import paths_cli.wizard

from functools import partial
from collections import namedtuple
import numpy as np

from paths_cli.wizard.parameters import (
    WizardObjectPlugin, FromWizardPrerequisite
)

from paths_cli.wizard.helper import Helper

from paths_cli.wizard.wrap_compilers import WrapCategory

try:
    import mdtraj as md
except ImportError:  # no-cov
    HAS_MDTRAJ = False
else:
    HAS_MDTRAJ = True

_ATOM_INDICES_HELP_STR = (
    "You should specify atom indicies enclosed in double brackets, e.g. "
    "[{list_range_natoms}]"
)

def mdtraj_atom_helper(wizard, user_input, n_atoms):  # no-cov
    wizard.say("You should specify atom indices enclosed in double "
               "brackets, e.g, [" + str(list(range(n_atoms))) + "]")
    # TODO: implement the following:
    # wizard.say("You can specify atoms either as atom indices (which count "
               # "from zero) or as atom labels of the format "
               # "CHAIN:RESIDUE-ATOM, e.g., '0:ALA1-CA' for the alpha carbon "
               # "of alanine 1 (this time counting from one, as in the PDB) "
               # "of the 0th chain in the topology. You can also use letters "
               # "for chain IDs, but note that A corresponds to the first "
               # "chain in your topology, even if its name in the PDB file "
               # "is B.")

TOPOLOGY_CV_PREREQ = FromWizardPrerequisite(
    name='topology',
    create_func=paths_cli.wizard.engines.ENGINE_PLUGIN,
    category='engines',
    obj_name='engine',
    n_required=1,
    say_create=("Hey, you need to define an MD engine before you create "
                "CVs that refer to it. Let's do that now!"),
    say_select=("You have defined multiple engines, and need to pick one "
                "to use to get a topology for your CV."),
    say_finish="Now let's get back to defining your CV.",
    load_func=lambda engine: engine.topology
)



def _get_topology(wizard):
    from paths_cli.wizard.engines import engines
    topology = None
    # TODO: this is very similar to get_missing_object, but has more
    # reporting; is there some way to add the reporting to
    # get_missing_object?
    if len(wizard.engines) == 0:
        # SHOULD NEVER GET HERE IF WIZARDS ARE DESIGNED CORRECTLY
        wizard.say("Hey, you need to define an MD engine before you "
                   "create CVs that refer to it. Let's do that now!")
        engine = engines(wizard)
        wizard.register(engine, 'engine', 'engines')
        wizard.say("Now let's get back to defining your CV.")
        topology = engine.topology
    elif len(wizard.engines) == 1:
        topology = list(wizard.engines.values())[0].topology
    else:
        wizard.say("You have defined multiple engines, and need to pick "
                   "one to use to get a the topology for your CV.")
        engine = wizard.obj_selector('engines', 'engine', engines)
        topology = engine.topology
        wizard.say("Now let's get back to defining your CV.")

    return topology

@get_object
def _get_atom_indices(wizard, topology, n_atoms, cv_user_str):
    helper = Helper(_ATOM_INDICES_HELP_STR.format(
        list_range_natoms=list(range(n_atoms))
    ))
    # switch to get_custom_eval
    atoms_str = wizard.ask(f"Which atoms do you want to {cv_user_str}?",
                           helper=helper)
    try:
        arr = mdtraj_parse_atomlist(atoms_str, n_atoms, topology)
    except Exception as e:
        wizard.exception(f"Sorry, I didn't understand '{atoms_str}'.", e)
        mdtraj_atom_helper(wizard, '?', n_atoms)
        return

    return arr

_MDTrajParams = namedtuple("_MDTrajParams", ['period', 'n_atoms',
                                             'kwarg_name', 'cv_user_str'])

def _mdtraj_cv_builder(wizard, prereqs, func_name):
    from openpathsampling.experimental.storage.collective_variables import \
            MDTrajFunctionCV
    dct = TOPOLOGY_CV_PREREQ(wizard)
    topology = dct['topology'][0]
    # TODO: add helpers
    (period_min, period_max), n_atoms, kwarg_name, cv_user_str = {
        'compute_distances': _MDTrajParams(
            period=(None, None),
            n_atoms=2,
            kwarg_name='atom_pairs',
            cv_user_str="measure the distance between"
        ),
        'compute_angles': _MDTrajParams(
            period=(-np.pi, np.pi),
            n_atoms=3,
            kwarg_name='angle_indices',
            cv_user_str="use to define the angle"
        ),
        'compute_dihedrals': _MDTrajParams(
            period=(-np.pi, np.pi),
            n_atoms=4,
            kwarg_name='indices',
            cv_user_str="use to define the dihedral angle"
        )
    }[func_name]

    indices = _get_atom_indices(wizard, topology, n_atoms=n_atoms,
                                cv_user_str=cv_user_str)
    func = getattr(md, func_name)
    kwargs = {kwarg_name: indices}
    return MDTrajFunctionCV(func, topology, period_min=period_min,
                            period_max=period_max, **kwargs)

_MDTRAJ_INTRO = "We'll make a CV that measures the {user_str}."

def _mdtraj_summary(cv):
    func = cv.func
    topology = cv.topology
    indices = list(cv.kwargs.values())[0]
    atoms_str = " ".join([str(topology.mdtraj.atom(i)) for i in indices[0]])
    summary = (f"  Function: {func.__name__}\n"
               f"     Atoms: {atoms_str}\n"
               f"  Topology: {repr(topology.mdtraj)}")
    return summary

if HAS_MDTRAJ:
    MDTRAJ_DISTANCE = WizardObjectPlugin(
        name='Distance',
        category='cvs',
        builder=partial(_mdtraj_cv_builder, func_name='compute_distances'),
        prerequisite=TOPOLOGY_CV_PREREQ,
        intro=_MDTRAJ_INTRO.format(user_str="distance between two atoms"),
        description="This CV will calculate the distance between two atoms.",
        summary=_mdtraj_summary,
    )

    MDTRAJ_ANGLE = WizardObjectPlugin(
        name="Angle",
        category='cvs',
        builder=partial(_mdtraj_cv_builder, func_name='compute_angles'),
        prerequisite=TOPOLOGY_CV_PREREQ,
        intro=_MDTRAJ_INTRO.format(user_str="angle made by three atoms"),
        description=...,
        summary=_mdtraj_summary,
    )

    MDTRAJ_DIHEDRAL = WizardObjectPlugin(
        name="Dihedral",
        category='cvs',
        builder=partial(_mdtraj_cv_builder, func_name='compute_dihedrals'),
        prerequisite=TOPOLOGY_CV_PREREQ,
        intro=_MDTRAJ_INTRO,
        description=...,
        summary=_mdtraj_summary,
    )

def _mdtraj_function_cv(wizard, cv_does_str, cv_user_prompt, func,
                        kwarg_name, n_atoms, period):
    from openpathsampling.experimental.storage.collective_variables import \
            MDTrajFunctionCV
    wizard.say(f"We'll make a CV that measures the {cv_does_str}.")
    period_min, period_max = period
    topology = _get_topology(wizard)
    indices = _get_atom_indices(wizard, topology, n_atoms=n_atoms,
                                cv_user_str=cv_user_prompt)
    kwargs = {kwarg_name: indices}
    atoms_str = " ".join([str(topology.mdtraj.atom(i)) for i in indices[0]])

    summary = ("Here's what we'll create:\n"
               f"  Function: {func.__name__}\n"
               f"     Atoms: {atoms_str}\n"
               f"  Topology: {repr(topology.mdtraj)}")
    wizard.say(summary)

    return MDTrajFunctionCV(func, topology, period_min=period_min,
                            period_max=period_max, **kwargs)

def distance(wizard):
    return _mdtraj_function_cv(
        wizard=wizard,
        cv_does_str="distance between two atoms",
        cv_user_prompt="measure the distance between",
        func=md.compute_distances,
        kwarg_name='atom_pairs',
        n_atoms=2,
        period=(None, None)
    )

def angle(wizard):
    return _mdtraj_function_cv(
        wizard=wizard,
        cv_does_str="angle made by three atoms",
        cv_user_prompt="use to define the angle",
        func=md.compute_angles,
        kwarg_name='angle_indices',
        n_atoms=3,
        period=(-np.pi, np.pi)
    )

def dihedral(wizard):
    return _mdtraj_function_cv(
        wizard=wizard,
        cv_does_str="dihedral made by four atoms",
        cv_user_prompt="use to define the dihedral angle",
        func=md.compute_dihedrals,
        kwarg_name='indices',
        n_atoms=4,
        period=(-np.pi, np.pi)
    )

def rmsd(wizard):
    raise NotImplementedError("RMSD has not yet been implemented")

def coordinate(wizard, prereqs=None):
    # TODO: atom_index should be from wizard.ask_custom_eval
    from openpathsampling.experimental.storage.collective_variables import \
            CoordinateFunctionCV
    atom_index = coord = None
    while atom_index is None:
        idx = wizard.ask("For which atom do you want to get the "
                         "coordinate? (counting from zero)")
        try:
            atom_index = int(idx)
        except Exception as e:
            wizard.exception("Sorry, I can't make an atom index from "
                             f"'{idx}'", e)

    while coord is None:
        xyz = wizard.ask("Which coordinate (x, y, or z) do you want for "
                         f"atom {atom_index}?")
        try:
            coord = {'x': 0, 'y': 1, 'z': 2}[xyz]
        except KeyError as e:
            wizard.bad_input("Please select one of 'x', 'y', or 'z'")

    cv = CoordinateFunctionCV(lambda snap: snap.xyz[atom_index][coord])
    return cv

COORDINATE_CV = WizardObjectPlugin(
    name="Coordinate",
    category="cvs",
    builder=coordinate,
    description=("Create a CV based on a specific coordinate (for a "
                 "specific atom)."),
)

CV_FROM_FILE = LoadFromOPS('cvs', 'CV')

SUPPORTED_CVS = {}

if HAS_MDTRAJ:
    SUPPORTED_CVS.update({
        'Distance': MDTRAJ_DISTANCE,
        'Angle': MDTRAJ_ANGLE,
        'Dihedral': MDTRAJ_DIHEDRAL,
        # 'RMSD': rmsd,
    })

SUPPORTED_CVS.update({
    'Coordinate': COORDINATE_CV,
    # 'Python script': ...,
    _load_label: CV_FROM_FILE,
})

CV_PLUGIN = WrapCategory(
    name='cvs',
    intro=("You'll need to describe your system in terms of collective "
           "variables (CVs). We'll use these variables to define things "
           "like stable states."),
    ask="What kind of CV do you want to define?",
    helper=("CVs are functions that map a snapshot to a number. If you "
            "have MDTraj installed, then I can automatically create "
            "several common CVs, such as distances and dihedrals.  But "
            "you can also create your own and load it from a file.")
)

def cvs(wizard):
    wizard.say("You'll need to describe your system in terms of "
               "collective variables (CVs). We'll use these to define "
               "things like stable states.")
    cv_names = list(SUPPORTED_CVS.keys())
    cv_type = wizard.ask_enumerate("What kind of CV do you want to "
                                   "define?", options=cv_names)
    cv = SUPPORTED_CVS[cv_type](wizard)
    return cv

# TEMPORARY
for plugin in [MDTRAJ_DISTANCE, MDTRAJ_ANGLE, MDTRAJ_DIHEDRAL,
               COORDINATE_CV, CV_FROM_FILE]:
    CV_PLUGIN.register_plugin(plugin)

if __name__ == "__main__":  # no-cov
    from paths_cli.wizard.wizard import Wizard
    wiz = Wizard({})
    cv = CV_PLUGIN(wiz)
    print(cv)

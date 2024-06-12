from paths_cli.compat.openmm import HAS_OPENMM

from paths_cli.wizard.parameters import ProxyParameter
from paths_cli.wizard.plugin_classes import WizardParameterObjectPlugin

from paths_cli.compiling.engines import OPENMM_PLUGIN as OPENMM_COMPILING

OPENMM_SERIALIZATION_URL = (
    "http://docs.openmm.org/latest/api-python/generated/"
    "openmm.openmm.XmlSerializer.html"
)

_WHERE_IS_XML = "Where is the XML file for your OpenMM {obj_type}?"
_XML_HELP = (
    "You can write OpenMM objects like systems and integrators to XML "
    "files using the XMLSerializer class. Learn more here:\n"
    + OPENMM_SERIALIZATION_URL
)

_OPENMM_REQS = ("To use OpenMM in the OPS wizard, you'll need to provide a "
                "file with topology information (usually a PDB), as well "
                "as XML versions of your OpenMM integrator and system "
                "objects.")

if HAS_OPENMM:
    OPENMM_PLUGIN = WizardParameterObjectPlugin.from_proxies(
        name="OpenMM",
        category="engine",
        description=("OpenMM is an GPU-accelerated library for molecular "
                     "dynamics. " + _OPENMM_REQS),
        intro=("Great! OpenMM gives you a lots of flexibility. " +
               _OPENMM_REQS),
        parameters=[
            ProxyParameter(
                name='topology',
                ask="Where is a PDB file describing your system?",
                helper=("We use a PDB file to set up the OpenMM simulation. "
                        "Please provide the path to your PDB file."),
            ),
            ProxyParameter(
                name='integrator',
                ask=_WHERE_IS_XML.format(obj_type='integrator'),
                helper=_XML_HELP,
            ),
            ProxyParameter(
                name='system',
                ask=_WHERE_IS_XML.format(obj_type="system"),
                helper=_XML_HELP,
            ),
            ProxyParameter(
                name='n_steps_per_frame',
                ask="How many MD steps per saved frame?",
                helper=("Your integrator has a time step associated with it. "
                        "We need to know how many time steps between the "
                        "frames we actually save during the run."),
            ),
            ProxyParameter(
                name='n_frames_max',
                ask="How many frames before aborting a trajectory?",
                helper=("Sometimes trajectories can get stuck in "
                        "unexpected basins. To prevent your trajectory "
                        "from running forever, you need to add a cutoff "
                        "trajectory length. This should be significantly "
                        "longer than you would expect a transition to "
                        "take."),
            ),
        ],
        compiler_plugin=OPENMM_COMPILING,
    )
else:
    OPENMM_PLUGIN = None


if __name__ == "__main__":
    from paths_cli.wizard.wizard import Wizard
    wizard = Wizard([])
    engine = OPENMM_PLUGIN(wizard)
    print(engine)

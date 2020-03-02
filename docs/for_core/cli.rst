.. _cli:

Command Line Interface
======================

A separate command line tool for OpenPathSamplng can be installed. It is
available via either ``conda`` (channel ``conda-forge``) or ``pip``, with
the package name ``openpathsampling-cli``.

Once you install this, you'll have access to the command
``openpathsampling`` in your shell (although we recommend aliasing that to
either ``paths`` or ``ops`` -- save yourself some typing!)

This command is a gateway to many subcommands, just like ``conda`` and
``pip`` (which have subcommands such as ``install``) or ``git`` (which has
subcommands such as ``clone`` or ``commit``). You can get a full listing all
the subcommands with ``openpathsampling --help``. For more information on
any given subcommand, use ``openpathsampling SUBCOMMAND --help``, replacing
``SUBCOMMAND`` with the subcommand you're interested in.

Here, we will provide a description of a few of the subcommands that the CLI
tool provides. This documentation may not be fully up-to-date with the more
recent releases of the CLI, so use the CLI help tools to get a fuller
understanding of what is included.

For more details on how the CLI interprets its arguments, and to learn how
to develop plugins for the CLI, see its documentation.  The CLI subcommands
are defined through a plugin system, which makes it very easy for developers
to create new subcommands.

* CLI documentation:
* CLI code repository:

Workflow with the CLI
---------------------

As always, the process of running a simulation is (1) set up the simulation;
(2) run the simulation; (3) analyze the simulation. The CLI is mainly
focused on step 2, although it also has tools that generally help with OPS
files.

To use it, you'll want to first set up 

Simulation Commands
-------------------

One of the main concepts when working with the CLI is that you can create
all the OPS simulation objects without running the simulation, save them in
an OPS storage file, and then load them again to actually run your
simulation. For simulation commands, the options all deal with loading
simulation objects from storage.

The simulation commands include ``equilibration``, ``pathsampling``, and
``simulation``.  These commands aren'y necessarily mutually exclusive: you
can accomplish an equilibration phase with any of them. The ``simulation``
command is the most general; if you've any :class:`.PathSimulator` object,
???

Here are some of the simulation commands implemented in the OPS CLI:

* ``pathsampling``: run path sampling with a given move scheme (suitable for
  custom TPS schemes as well as TIS/RETIS); must provide move scheme,
  iniital conditions,  and number of MC steps on command line
* ``simulation``: run arbitrary OPS simulator (including committor and
  related); must provide a simulator object and number of steps on the
  command line
* ``visit-all``: create initial trajectories by running MD until all states
  have been visited (works for MSTIS or any 2-state system); must provide
  states, engine, and initial snapshot on command line

.. TODO figure showing how these all work -- what is needed for each, what
   is implicit

Miscellaneous Commands
----------------------

Even for users who prefer to develop their OPS projects entirely in Python,
foregoing the CLI tools to run simulations, some of the "miscellaneous"
commands are likely to be quite useful. Here are some that are available in
the CLI:

* ``contents``: list all the named objects in an OPS storage, organized by
  store (type); this is extremely useful to get the name of an object to use
  as command-line input to one of the simulation scripts
.. * ``strip-snapshots``: create a copy of the input storage file with the
  details (coordinates/velocities) of all snapshots removed; this allows you
  to make a much smaller copy (with results of CVs) to copy back to a local
  computer for analysis
* ``append`` : add an object from once OPS storage into another one; this is
  useful for getting everything into a single file before running a
  simulation

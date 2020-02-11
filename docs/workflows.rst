.. _workflows:

Writing Workflow Commands
=========================

In general, we don't recommend "one-pot cooking," where you start with a PDB
and end with path sampling results, without stopping to look at any
intermediate results. Aggressive approaches to create an initial trajectory
can go wrong, and if you use a month of computer time running a path
sampling simulation from a trajectory that is unrealistic (and took at most
a day to generate), then you've wasted a lot of time. We recommend doing
sanity checks on intermediate stages to ensure that you're getting
reasonable behavior.

That said, the OpenPathSampling CLI makes it very easy for you to create
your own fully automated workflow protocol, and to launch it from a single
command on the command line. Workflows can be useful for standardizing a
simulation protocol, and writing the workflow as a plugin for the OPS CLI
makes it easy to share that protocol with others.

There are two practices that we recommend (and which we follow) that
facilitate this:

1. Split your plugin code into a main function, written purely for
   OpenPathSampling, and an adapter function that gets the information from
   the CLI.
2. The pure-OPS main function should return the tuple ``(results,
   simulation)``, where ``results`` are the final results of the command
   (the sample set or trajectory that represents the final state of your
   simulation), and ``simulation`` is the ``PathSimulator`` subclass your
   created, or ``None`` if that is not relevant.

This combination makes it extremely easy to create workflow commands from
existing OPS CLI functions. The workflow just involves chaining together the
outputs/inputs from the individual pure-OPS main functions. By creating a
CLI adapter for the workflow, you suddenly have a command for your workflow!

We provide an example of this in ``example_plugins/one_pot_tps.py``. This is
a workflow that generates an initial trajectory using the ``main`` functionf
rom the ``visit-all`` comamnd, performs a pre-defined equilibration TPS run,
and finally does a production TPS run.

You can immediately enable that (or any other) plugin by placing it in your
``~/.openpathsampling/cli-plugins`` directory.

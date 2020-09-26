.. OpenPathSampling CLI documentation master file, created by
   sphinx-quickstart on Sun Dec  8 01:32:00 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

OpenPathSampling CLI
====================

This is documentation for the OpenPathSampling CLI. Most of this is intended
for developers. Basic usage documentation is the in the main OPS docs,
although a few things here might be relevant to users (e.g., the details
of how the built-in parameters interpret user-provided arguments, discussed
in :ref:`interpretation`, or the :ref:`full listing for CLI commands and
arguments <full_cli>`).

The main purpose of this documentation is for people who want to create
their own plugins for the OpenPathsampling CLI. Note that, because the OPS
CLI uses a flexible dynamic plugin structure, installing a plugin is as easy
as adding the plugin file to ``~/.openpathsampling/cli-plugins/``. See also
:ref:`plugins`.

Developing for the OPS CLI is pretty easy. The mains ideas are:

* **Most of the business logic is elsewhere.** There shouldn't be anything
  in this repository that involved putting together new move types or
  anything like that. All of that belongs in external repositories (such as
  OPS itself). All functionality in the CLI should be available in a
  library; the CLI is a thin wrapper over the library.
* **Reuse existing parameters whenever possible.** This ensures that
  option labels and help strings are constant across the suite of
  tools. It also ensures that behavior remains consistent: for example, the
  steps that we go through in searching for an initial trajectory is the
  same regardless of the type of simulation.


A note on testing:

Because the CLI is a thin wrapper over the library, we can also be
relatively lax in testing. We thoroughly test the OPS loading parameters.
But the actual commands are just chaining together existing well-tested OPS
functions, and so we just do smoke tests for the commands.

Essentially, the testing purpose that these serve would be as system tests
for OPS, and OPS already has system tests. So we smoke test to make sure the
code is sane. Again, this is only acceptable because the commands are thin
wrappers around well-tested OPS code.

.. note::

   The project is called OpenPathSampling CLI, and the packages (PyPI and
   conda-forge) are called ``openpathsampling-cli``. However, the name you
   use to import the package is ``paths_cli``, as a nod to the encouraged
   habit of importing openpathsampling as ``paths``.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   interpretation
   plugins
   parameters
   workflows
   full_cli
   api/index


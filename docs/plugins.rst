.. _plugins:

Plugin Infrastructure
=====================

All subcommands to the OpenPathSampling CLI use a plugin infrastructure.
There are two possible ways to distribute plugins (file plugins and
namespace plugins), but a given plugin script could be distributed either
way. 

Writing a command plugin
------------------------

To write an OPS command plugin, you simply need to create an instance of
:class:`paths_cli.OPSCommandPlugin` and to install the module in a location
where the CLI knows to look for it. The input parameters to
``OPSCommandPlugin`` are:

* ``command``: This is the main CLI function for the subcommand. It must be
  decorated as a ``click.command``.
* ``section``: This is a string to determine where to show it in help (what
  kind of command it is).  Valid values are ``"Simulation"``,
  ``"Analysis"``, ``"Miscellaneous"``, or ``"Workflow"``. If ``section``
  doesn't have one of these values, it won't show in ``openpathsampling
  --help``, but might still be usable. If your command doesn't show in the
  help, carefully check your spelling of the ``section`` variable.
* ``requires_ops`` (optional, default ``(1, 0)``): Minimum allowed version
  of OpenPathSampling. Note that this is currently informational only, and
  has no effect on functionality.
* ``requires_cli`` (optional, default ``(0, 3)``): Minimum allowed version
  of the OpenPathSampling CLI.  Note that this is currently informational
  only, and has no effect on functionality.


If you distribute your plugin as a file-based plugin, be aware that it must
be possible to ``exec`` it in an empty namespace (mainly, this can mean no
relative imports).

As a suggestion, I (DWHS) tend to structure my plugins as follows:

.. code:: python

    @click.command("plugin", short_help="brief description")
    @PARAMETER.clicked(required)
    def plugin(parameter):
        plugin_main(PARAMETER.get(parameter))

    def plugin_main(parameter):
        import openpathsampling as paths
        # do the real stuff with OPS
        ...
        return final_status, simulation

    PLUGIN = OPSCommandPlugin(command=plugin, section="MySection")

The basic idea is that there's a ``plugin_main`` function that is based on
pure OPS, using only inputs that OPS can immediately understand (no need to
process the command line). This is easy to develop/test with OPS. Then
there's a wrapper function whose sole purpose is to convert the command line
parameters to something OPS can understand (using the ``get`` method). This
wrapper is the ``command`` in you ``OPSCommandPlugin``. Also provide an
allowed ``section``, and the plugin is ready!

The result is that plugins are astonishingly easy to develop, once you have
the scientific code implemented in a library. This structure also makes it
very easy to test the plugins: a mock replaces the ``plugin_main`` in
``plugin`` to check that the integration works, and then a simple smoke test
for the ``plugin_main`` is sufficient, since the core code should already be
well-tested.

Note that we recommend that the import of OpenPathSampling only be done
inside the ``plugin_main`` function. Although this is contrary to normal
Python practice, we do this because tools like tab-autocomplete require
that you run the program each time. The import of OPS is rather slow, so we
delay it until it is needed, keeping the CLI interface fast and responsive.

Finally, the ``plugin_main`` function returns some sort of final status and
the simulation object that was created (or ``None`` if there wasn't one).
This makes it very easy to chain multiple main functions to make a workflow.


Distributing file plugins
-------------------------

Once you have a plugin module written, the easiest way to install it is to
put it in your ``~/.openpathsampling/cli_plugins/`` directory. This is the
file-based plugin distribution mechanism -- you send the file to someone,
and they put in that directory.

This is great for plugins shared in a single team, or for creating
reproducible workflows that aren't intended for wide distribution.


Distributing namespace plugins
------------------------------

If the plugin is part of a larger Python package, or if it is important to
track version numbers or to be able to change which plugins are installed
in particular Python environments, the namespace distribution mechanism is a
better choice. We use `native namespace packages`_, which is a standard way
of making plugins in Python. Plugins should be in the ``paths_cli_plugins``
namespace.

.. _native namespace packages:
  https://packaging.python.org/guides/packaging-namespace-packages/#native-namespace-packages


.. _plugins:

Plugin Infrastructure
=====================

All subcommands to the OpenPathSampling CLI use a plugin infrastructure.
They simply need to be Python modules, following a few rules, that are
placed into the user's ``~/.openpathsampling/cli-plugins/`` directory.

Technically, the code searches two directories for plugins: first,
``$DIRECTORY/commands``, where ``$DIRECTORY`` is the directory where the
main OPS CLI script has been installed (i.e., the directory that corresponds
to the Python package ``paths_cli``). This is where the default commands are
kept. Then it searches the user directory. Duplicate commands will lead to
errors when running the CLI, as you can't register the same name twice.

Other than being in the right place, the script must do the following:

* It must be possible to ``exec`` it in an empty namespace (mainly, this
  can mean no relative imports).
* It must define a variable ``CLI`` that is the main CLI function is
  assigned to.
* It must define a variable ``SECTION`` to determine where to show it in
  help (what kind of command it is). Valid values are ``"Simulation"``,
  ``"Analysis"``, ``"Miscellaneous"``, or ``"Workflow"``. If ``SECTION`` is
  defined but doesn't have one of these values, it won't show in
  ``openpathsampling --help``, but might still be usable. If your command
  doesn't show in the help, carefully check your spelling of the ``SECTION``
  variable.

As a suggestion, I (DWHS) tend to structure my plugins as follows:

.. code:: python

    @PARAMETER.clicked(required)
    def plugin(parameter):
        plugin_main(PARAMETER.get(parameter))

    def plugin_main(parameter):
        import openpathsampling as paths
        # do the real stuff with OPS
        ...

    CLI = plugin
    SECTION = "MySection"

The basic idea is that there's a ``plugin_main`` function that is based on
pure OPS, using only inputs that OPS can immediately understand (no need to
go to storage, etc). This is easy to develop/test with OPS. Then there's a
wrapper function whose sole purpose is to convert the command line
parameters to something OPS can understand (using the ``get`` method). This
wrapper is the ``CLI`` variable. Give it an allowed ``SECTION``, and the
plugin is ready!

The result is that plugins are astonishingly easy to develop, once you have
the scientific code implemented in a library.

Note that we recommend that the import of OpenPathSampling only be done
inside the ``plugin_main`` function. Although this is contrary to normal
Python practice, we do this because tools like tab-autocomplete require
that you run the program each time. The import of OPS is rather slow, so we
delay it until it is needed, keeping the CLI interface fast and responsive.

.. TODO : look into having the plugin auto-installed using setuptools

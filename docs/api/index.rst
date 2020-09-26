.. _api:

API
===

.. currentmodule:: paths_cli

CLI and Plugins
---------------

.. autosummary::
    :toctree: generated

    OpenPathSamplingCLI
    plugin_management.CLIPluginLoader
    plugin_management.FilePluginLoader
    plugin_management.NamespacePluginLoader


Parameter Decorators
--------------------

These are the functions used to create the reusable parameter decorators.
Note that you will probably never need to use these; instead, use the
existing parameter decorators.

.. autosummary::
    :toctree: generated

    param_core.Option
    param_core.Argument
    param_core.AbstractLoader
    param_core.StorageLoader
    param_core.OPSStorageLoadNames
    param_core.OPSStorageLoadSingle

Search strategies
-----------------

These are the various strategies for finding objects in a storage, in
particular if we have to guess because the user didn't provide an explicit
choice or didn't tag.

.. autosummary::
    :toctree: generated

    param_core.Getter
    param_core.GetByName
    param_core.GetByNumber
    param_core.GetPredefinedName
    param_core.GetOnly
    param_core.GetOnlyNamed
    param_core.GetOnlySnapshot


Commands
--------

.. autosummary::
    :toctree: generated
    :recursive:

    commands.visit_all
    commands.equilibrate
    commands.pathsampling
    commands.append
    commands.contents

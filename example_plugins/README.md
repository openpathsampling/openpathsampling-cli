# Example Plugins

This directory includes a few example plugins for the OpenPathSampling CLI.
There are various reasons these are not included in the default CLI, including:

* they reproduce existing functionality, and would add confusion to the user
  experience (`tps.py`)
* they don't fit into the overall philosophy of the CLI, which intends to
  provide individual tools instead of "one pot cooking" scripts that do
  everything in one go (`one_pot_tps.py`).


We distribute them here mainly to provide additional examples so
users/developers can write their own plugins.  Distributing these also makes it
easy for users to use these specific workflows, without adding confusion for
all users by making too many commands.

To install a plugin, all you need to do is to copy (or symlink) the file here
into your `~/.openpathsampling/cli-plugins/` directory.

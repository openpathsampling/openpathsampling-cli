import pytest
from unittest.mock import MagicMock

import pathlib
import importlib

import paths_cli
from paths_cli.plugin_management import *

# need to check that CLI is assigned to correct type
import click

def test_ops_plugin():
    plugin = OPSPlugin(requires_ops=(1,2), requires_cli=(0,4))
    assert plugin.requires_ops == (1, 2)
    assert plugin.requires_cli == (0, 4)
    assert plugin.requires_lib == (1, 2)

class PluginLoaderTest(object):
    def setup_method(self):
        self.expected_section = {'pathsampling': "Simulation",
                                 'contents': "Miscellaneous"}

    def _make_candidate(self, command):
        raise NotImplementedError()

    @pytest.mark.parametrize('command', ['pathsampling', 'contents'])
    def test_find_candidates(self, command):
        candidates  = self.loader._find_candidates()
        str_candidates = str([c for c in candidates])
        assert str(self._make_candidate(command)) in str_candidates

    @pytest.mark.parametrize('command', ['pathsampling', 'contents'])
    def test_make_nsdict(self, command):
        candidate = self._make_candidate(command)
        nsdict = self.loader._make_nsdict(candidate)
        plugin = nsdict['PLUGIN']
        assert plugin.section == self.expected_section[command]
        assert isinstance(plugin.command, click.Command)

    @pytest.mark.parametrize('command', ['pathsampling', 'contents'])
    def test_call(self, command):
        plugins = self.loader()
        plugin_dict = {p.name: p for p in plugins}
        plugin = plugin_dict[command]
        assert plugin.name == command
        assert str(plugin.location) == str(self._make_candidate(command))
        assert isinstance(plugin.func, click.Command)
        assert plugin.section == self.expected_section[command]
        assert plugin.plugin_type == self.plugin_type


class TestFilePluginLoader(PluginLoaderTest):
    def setup_method(self):
        super().setup_method()
        # use our own commands dir as a file-based plugin
        cmds_init = pathlib.Path(paths_cli.commands.__file__).resolve()
        self.commands_dir = cmds_init.parent
        self.loader = FilePluginLoader(self.commands_dir, OPSCommandPlugin)
        self.plugin_type = 'file'

    def _make_candidate(self, command):
        return self.commands_dir / (command + ".py")


class TestNamespacePluginLoader(PluginLoaderTest):
    def setup_method(self):
        super().setup_method()
        self.namespace = "paths_cli.commands"
        self.loader = NamespacePluginLoader(self.namespace, OPSCommandPlugin)
        self.plugin_type = 'namespace'

    def _make_candidate(self, command):
        name = self.namespace + "." + command
        return importlib.import_module(name)

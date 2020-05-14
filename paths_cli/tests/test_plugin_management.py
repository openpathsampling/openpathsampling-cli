import pytest
from unittest.mock import MagicMock

import pathlib
import importlib

import paths_cli
from paths_cli.plugin_management import *

# need to check that CLI is assigned to correct type
import click

class TestCLIPluginLoader(object):
    def setup(self):
        class MockPlugin(object):
            def get_dict(self):
                return {
                    'CLI': self.foo,
                    'SECTION': "FooSection"
                }

            def foo():
                pass

        self.plugin = MockPlugin()
        self.loader = CLIPluginLoader(plugin_type="test", search_path="foo")
        self.loader._make_nsdict = MockPlugin.get_dict
        self.loader._find_candidates = MagicMock(return_value=[self.plugin])

    @pytest.mark.parametrize('contains', ([], ['cli'], ['sec'],
                                          ['cli', 'sec']))
    def test_validate(self, contains):
        expected = len(contains) == 2  # only case where we expect correct
        dct = {'cli': self.plugin.foo, 'sec': "FooSection"}
        fullnames = {'cli': "CLI", 'sec': "SECTION"}
        nsdict = {fullnames[obj]: dct[obj] for obj in contains}

        assert CLIPluginLoader._validate(nsdict) == expected

    def test_find_valid(self):
        # smoke test for the procedure
        expected = {self.plugin: self.plugin.get_dict()}
        assert self.loader._find_valid() == expected


class PluginLoaderTest(object):
    def setup(self):
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
        assert nsdict['SECTION'] == self.expected_section[command]
        assert isinstance(nsdict['CLI'], click.Command)

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
    def setup(self):
        super().setup()
        # use our own commands dir as a file-based plugin
        cmds_init = pathlib.Path(paths_cli.commands.__file__).resolve()
        self.commands_dir = cmds_init.parent
        self.loader = FilePluginLoader(self.commands_dir)
        self.plugin_type = 'file'

    def _make_candidate(self, command):
        return self.commands_dir / (command + ".py")

    def test_get_command_name(self):
        # this may someday get parametrized, set it up to make it easy
        filename = "/foo/bar/baz_qux.py"
        expected = "baz-qux"
        assert self.loader._get_command_name(filename) == expected


class TestNamespacePluginLoader(PluginLoaderTest):
    def setup(self):
        super().setup()
        self.namespace = "paths_cli.commands"
        self.loader = NamespacePluginLoader(self.namespace)
        self.plugin_type = 'namespace'

    def _make_candidate(self, command):
        name = self.namespace + "." + command
        return importlib.import_module(name)

    def test_get_command_name(self):
        loader = NamespacePluginLoader('foo.bar')
        candidate = MagicMock(__name__="foo.bar.baz_qux")
        expected = "baz-qux"
        assert loader._get_command_name(candidate) == expected

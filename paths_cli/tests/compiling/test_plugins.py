import pytest
from paths_cli.compiling.plugins import *
from unittest.mock import Mock

class TestCompilerPlugin:
    def setup(self):
        self.plugin_class = Mock(compiler_name='foo')
        self.plugin = CompilerPlugin(self.plugin_class)
        self.aliased_plugin = CompilerPlugin(self.plugin_class,
                                             aliases=['bar'])

    @pytest.mark.parametrize('plugin_type', ['basic', 'aliased'])
    def test_init(self, plugin_type):
        plugin = {'basic': self.plugin,
                  'aliased': self.aliased_plugin}[plugin_type]
        expected_alias = {'basic': [], 'aliased': ['bar']}[plugin_type]
        assert plugin.aliases == expected_alias
        assert plugin.plugin_class == self.plugin_class
        assert plugin.name == 'foo'
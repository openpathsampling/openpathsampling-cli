import pytest
from click.testing import CliRunner

import json

from paths_cli.commands.compile import *

def test_import_module():
    new_json = import_module('json')
    assert new_json is json

def test_import_module_error():
    with pytest.raises(MissingIntegrationError, match="Unable to find"):
        import_module('foobarbazqux')

_BASIC_DICT = {'foo': ['bar', {'baz': 10}], 'qux': 'quux', 'froob': 0.5}

def _std_dump(module):
    return module.dump

@pytest.mark.parametrize('mod_name', ['json', 'yaml'])
def test_loaders(mod_name, tmpdir):
    mod = pytest.importorskip(mod_name)
    dump_getter = {
        'json': _std_dump,
        'yaml': _std_dump,
        'toml': _std_dump,
    }[mod_name]
    loader = {
        'json': load_json,
        'yaml': load_yaml,
        # 'toml': load_toml,
    }[mod_name]
    dump = dump_getter(mod)
    filename = tmpdir.join("temp." + mod_name)
    with open(filename, 'a+') as fp:
        dump(_BASIC_DICT, fp)
        fp.seek(0)
        assert loader(fp) == _BASIC_DICT

@pytest.mark.parametrize('ext', ['jsn', 'json', 'yaml', 'yml'])
def test_select_loader(ext):
    if ext in ['jsn', 'json']:
        expected = load_json
    elif ext in ['yml', 'yaml']:
        expected = load_yaml

    assert select_loader("filename." + ext) is expected
    pass

def test_select_loader_error():
    with pytest.raises(RuntimeError, match="Unknown file extension"):
        select_loader('foo.bar')

def test_compile():
    pass

import pytest
from click.testing import CliRunner

import json
import shutil

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

def test_select_loader_error():
    with pytest.raises(RuntimeError, match="Unknown file extension"):
        select_loader('foo.bar')

def test_compile(ad_openmm, test_data_dir):
    runner = CliRunner()
    setup = test_data_dir / "setup.yml"
    shutil.copy2(str(setup), ad_openmm)
    with runner.isolated_filesystem(temp_dir=ad_openmm):
        import os
        cwd = os.getcwd()
        files = [setup, ad_openmm / "ad.pdb", ad_openmm / "system.xml",
                 ad_openmm / "integrator.xml"]
        for filename in files:
            shutil.copy2(str(filename), cwd)
        pytest.skip()  # TODO: right now we're not building the parsers
        result = runner.invoke(
            compile_,
            ['setup.yml', '-o', str(ad_openmm / 'setup.db')]
        )
        assert result.exit_code == 0
        from openpathsampling.experimental.storage import (
            Storage, monkey_patch_all)
        st = Storage('setup.db', mode='r')

        # smoke tests that we can reload things
        engine = st.engines['engine']
        phi = st.cvs['phi']
        C_7eq = st.volumes['C_7eq']
        pytest.skip()

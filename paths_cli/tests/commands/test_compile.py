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

def test_import_module_install_suggestion():
    with pytest.raises(MissingIntegrationError, match="Please install"):
        import_module('foobarbazqux', install='foobarbazqux')

_BASIC_DICT = {'foo': ['bar', {'baz': 10}], 'qux': 'quux', 'froob': 0.5}

def _std_dump(module):
    return module.dump

@pytest.mark.parametrize('mod_name', ['json', 'yaml'])
def test_loaders(mod_name, tmpdir):
    mod = pytest.importorskip(mod_name)
    dump_getter = {
        'json': _std_dump,
        'yaml': _std_dump,
        # 'toml': _std_dump,
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
    # this is a smoke test to check that, given a correct YAML file, we can
    # compile the yaml into a db file, and then reload (some of) the saves
    # objects from the db.
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
        # pytest.skip()  # TODO: compiler aliases don't work yet
        result = runner.invoke(
            compile_,
            ['setup.yml', '-o', str(ad_openmm / 'setup.db')]
        )
        if result.exc_info:  # -no-cov-
            # this only runs in the event of an error (to provide a clearer
            # failure)  (TODO: change this up a little maybe? re-raise the
            # error?)
            import traceback
            traceback.print_tb(result.exc_info[2])
            print(result.exception)
            print(result.exc_info)
            print(result.output)
        assert os.path.exists(str(ad_openmm / 'setup.db'))
        import openpathsampling as paths
        from openpathsampling.experimental.storage import (
            Storage, monkey_patch_all)
        # TODO: need to do the temporary monkey patch here
        st = Storage(str(ad_openmm / 'setup.db'), mode='r')

        # smoke tests that we can reload things
        print("Engines:", len(st.engines), [e.name for e in st.engines])
        engine = st.engines['engine']
        phi = st.cvs['phi']
        C_7eq = st.volumes['C_7eq']
        from openpathsampling.experimental.storage.monkey_patches import unpatch
        paths = unpatch(paths)
        paths.InterfaceSet.simstore = False
        # TODO: this lines won't be necessary once OPS releases contain
        # openpathsampling/openpathsampling#1065
        import importlib
        importlib.reload(paths.netcdfplus)
        importlib.reload(paths.collectivevariable)
        importlib.reload(paths.collectivevariables)
        importlib.reload(paths)

import pytest
from unittest import mock

import openpathsampling as paths

from paths_cli.tests.wizard.mock_wizard import mock_wizard

from paths_cli.wizard.load_from_ops import (
    _get_ops_storage, _get_ops_object, load_from_ops
)

# for some reason I couldn't get these to work with MagicMock
class NamedObj:
    def __init__(self, name):
        self.name = name
        self.is_named = True

class FakeStore:
    def __init__(self, objects):
        self._objects = objects
        self._named_objects = {obj.name: obj for obj in objects}

    # leaving this commented out... it doesn't seem to be used currently,
    # but if it is needed in the future, this should be the implementation
    # def __getitem__(self, key):
    #     if isinstance(key, int):
    #         return self._objects[key]
    #     elif isinstance(key, str):
    #         return self._named_objects[key]
    #     else:  # -no-cov-
    #         raise TypeError("Huh?")

    def __iter__(self):
        return iter(self._objects)

class FakeStorage:
    def __init__(self, foo):
        self.foo = foo

@pytest.fixture
def ops_file_fixture():
    # store name 'foo', objects named 'bar', 'baz'
    bar = NamedObj('bar')
    baz = NamedObj('baz')
    foo = FakeStore([bar, baz])
    storage = FakeStorage(foo)
    return storage


@pytest.mark.parametrize('with_failure', [False, True])
def test_get_ops_storage(tmpdir, with_failure):
    fake_file = tmpdir / 'foo.db'
    fake_file.write_text('bar', 'utf-8')

    failure_text = ['baz.db'] if with_failure else []
    wizard = mock_wizard(failure_text + [str(fake_file)])

    with mock.patch('paths_cli.wizard.load_from_ops.INPUT_FILE',
                    new=mock.Mock(get=open)):
        storage = _get_ops_storage(wizard)
    assert storage.read() == 'bar'
    if with_failure:
        assert 'something went wrong' in wizard.console.log_text
    else:
        assert 'something went wrong' not in wizard.console.log_text

@pytest.mark.parametrize('with_failure', [False, True])
def test_get_ops_object(ops_file_fixture, with_failure):
    failure_text = ['qux'] if with_failure else []
    wizard = mock_wizard(failure_text + ['bar'])
    obj = _get_ops_object(wizard, ops_file_fixture,
                          store_name='foo',
                          obj_name='FOOMAGIC')
    assert isinstance(obj, NamedObj)
    assert obj.name == 'bar'
    log = wizard.console.log_text
    assert 'name of the FOOMAGIC' in log
    fail_msg = 'not a valid option'
    if with_failure:
        assert fail_msg in log
    else:
        assert fail_msg not in log

def test_load_from_ops(ops_file_fixture):
    wizard = mock_wizard(['anyfile.db', 'bar'])
    with mock.patch('paths_cli.wizard.load_from_ops.INPUT_FILE.get',
                    mock.Mock(return_value=ops_file_fixture)):
        obj = load_from_ops(wizard, 'foo', 'FOOMAGIC')

    assert isinstance(obj, NamedObj)
    assert obj.name == 'bar'

import pytest
from unittest import mock
from paths_cli.tests.wizard.mock_wizard import (
    MockConsole, make_mock_wizard, make_mock_retry_wizard
)
import pathlib

from openpathsampling.experimental.storage.collective_variables import \
        CoordinateFunctionCV

from paths_cli.wizard.wizard import *
from paths_cli.wizard.steps import SINGLE_ENGINE_STEP

import openpathsampling as paths

class MockStore:
    def __init__(self):
        self.all_entries = []
        self.name_dict = {}

    def register(self, obj):
        self.all_entries.append(obj)
        if obj.is_named:
            self.name_dict[obj.name] = obj

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.all_entries[key]
        else:
            return self.name_dict[key]

    def __len__(self):
        return len(self.all_entries)

class MockStorage:
    def __init__(self):
        self.engines = MockStore()
        self.volumes = MockStore()
        self.cvs = MockStore()
        self.networks = MockStore()
        self.schemes = MockStore()

    def save(self, obj):
        class_to_store = {
            paths.engines.DynamicsEngine: self.engines,
            paths.Volume: self.volumes,
            CoordinateFunctionCV: self.cvs,
            paths.TransitionNetwork: self.networks,
            paths.MoveScheme: self.schemes,
        }
        for cls in class_to_store:
            if isinstance(obj, cls):
                store = class_to_store[cls]
                break

        store.register(obj)


class TestWizard:
    def setup_method(self):
        self.wizard = Wizard([])

    def test_initialization(self):
        wizard = Wizard([SINGLE_ENGINE_STEP])
        assert wizard.requirements == {'engine': ('engines', 1, 1)}

    def test_ask(self):
        console = MockConsole('foo')
        self.wizard.console = console
        result = self.wizard.ask('bar')
        assert result == 'foo'
        assert 'bar' in console.log_text

    def test_ask_help(self):
        console = MockConsole(['?helpme', 'foo'])
        self.wizard.console = console
        def helper(result):
            return f"You said: {result[1:]}"

        result = self.wizard.ask('bar', helper=helper)
        assert result == 'foo'
        assert 'You said: helpme' in console.log_text

    @pytest.mark.parametrize('autohelp', [True, False])
    def test_ask_empty(self, autohelp):
        # if the use response in an empty string, we should repeat the
        # question (possible giving autohelp). This fixes a regression where
        # an empty string would cause an uncaught exception.
        console = MockConsole(['', 'foo'])
        self.wizard.console = console
        result = self.wizard.ask("question",
                                 helper=lambda x: "say_help",
                                 autohelp=autohelp)
        assert result == "foo"
        if autohelp:
            assert "say_help" in self.wizard.console.log_text

    def _generic_speak_test(self, func_name):
        console = MockConsole()
        self.wizard.console = console
        func = getattr(self.wizard, func_name)
        func('foo')
        assert 'foo' in console.log_text

    def test_say(self):
        self._generic_speak_test('say')

    def test_start(self):
        self._generic_speak_test('start')

    def test_bad_input(self):
        self._generic_speak_test('bad_input')

    @pytest.mark.parametrize('user_inp', ['int', 'str', 'help', 'bad'])
    def test_ask_enumerate_dict(self, user_inp):
        inputs = {'int': ["1"],
                  'str': ["bar"],
                  'help': ["?", "1"],
                  "bad": ["99", "1"]}[user_inp]
        console = MockConsole(inputs)
        self.wizard.console = console
        selected = self.wizard.ask_enumerate_dict(
            question="foo",
            options={"bar": "bar_func", "baz": "baz_func"}
        )
        assert selected == "bar_func"
        assert 'foo' in console.log_text
        assert '1. bar' in console.log_text
        assert '2. baz' in console.log_text
        assert console.input_call_count == len(inputs)
        if user_inp == 'help':
            assert "no help available" in console.log_text
        elif user_inp == "bad":
            assert "'99'" in console.log_text
            assert "not a valid option" in console.log_text

    @pytest.mark.parametrize('bad_choice', [False, True])
    def test_ask_enumerate(self, bad_choice):
        inputs = {False: '1', True: ['10', '1']}[bad_choice]
        console = MockConsole(inputs)
        self.wizard.console = console
        selected = self.wizard.ask_enumerate('foo', options=['bar', 'baz'])
        assert selected == 'bar'
        assert 'foo' in console.log_text
        assert '1. bar' in console.log_text
        assert '2. baz' in console.log_text
        assert console.input_call_count == len(inputs)
        if bad_choice:
            assert "'10'" in console.log_text
            assert 'not a valid option' in console.log_text
        else:
            assert "'10'" not in console.log_text
            assert 'not a valid option' not in console.log_text

    def test_ask_load(self):
        console = MockConsole(['100'])
        self.wizard.console = console
        loaded = self.wizard.ask_load("foo", int)
        assert loaded == 100
        assert "foo" in console.log_text

    def test_ask_load_error(self):
        console = MockConsole(["abc", "100"])
        self.wizard.console = console
        loaded = self.wizard.ask_load("foo", int)
        assert loaded == 100
        assert "foo" in console.log_text
        assert "ValueError" in console.log_text
        assert "base 10" in console.log_text

    @pytest.mark.parametrize('inputs, type_, expected', [
        ("2+2", int, 4), ("0.1 * 0.1", float, 0.1*0.1), ("2.4", int, 2)
    ])
    def test_ask_custom_eval(self, inputs, type_, expected):
        console = MockConsole(inputs)
        self.wizard.console = console
        result = self.wizard.ask_custom_eval('foo', type_=type_)
        assert result == expected
        assert console.input_call_count == 1
        assert 'foo' in console.log_text

    def test_ask_custom_eval_bad_type(self):
        console = MockConsole(['"bar"', '2+2'])
        self.wizard.console = console
        result = self.wizard.ask_custom_eval('foo')
        assert result == 4
        assert console.input_call_count == 2
        assert "I couldn't understand" in console.log_text
        assert "ValueError" in console.log_text

    def test_ask_custom_eval_bad_input(self):
        console = MockConsole(['bar', '2+2'])
        self.wizard.console = console
        result = self.wizard.ask_custom_eval('foo')
        assert result == 4
        assert console.input_call_count == 2
        assert "I couldn't understand" in console.log_text
        assert "NameError" in console.log_text

    @pytest.mark.parametrize('inputs,expected', [('1', 'bar'),
                                                 ('2', 'new')])
    def test_obj_selector(self, inputs, expected):
        create_func = lambda wiz: 'new'
        console = MockConsole(inputs)
        self.wizard.console = console
        self.wizard.cvs = {'foo': 'bar'}
        def mock_register(obj, name, store):
            console.print("registered")
            return obj
        self.wizard.register = mock_register
        sel = self.wizard.obj_selector('cvs', "CV", create_func)
        assert sel == expected
        assert "CV" in console.log_text
        if inputs == '2':
            assert "registered" in console.log_text

    def test_exception(self):
        console = MockConsole()
        self.wizard.console = console
        err = RuntimeError("baz")
        self.wizard.exception('foo', err)
        assert 'foo' in console.log_text
        assert "RuntimeError: baz" in console.log_text

    def test_name(self):
        wizard = make_mock_wizard('foo')
        cv = CoordinateFunctionCV(lambda s: s.xyz[0][0])
        assert not cv.is_named
        result = wizard.name(cv, obj_type="CV", store_name="cvs")
        assert result is cv
        assert result.is_named
        assert result.name == 'foo'

    def test_name_exists(self):
        wizard = make_mock_retry_wizard(['foo', 'bar'])
        wizard.cvs['foo'] = 'placeholder'
        cv = CoordinateFunctionCV(lambda s: s.xyz[0][0])
        assert not cv.is_named
        result = wizard.name(cv, obj_type="CV", store_name="cvs")
        assert result is cv
        assert result.is_named
        assert result.name == 'bar'
        assert wizard.console.input.call_count == 2


    @pytest.mark.parametrize('named', [True, False])
    def test_register(self, named):
        cv = CoordinateFunctionCV(lambda s: s.xyz[0][0])
        if named:
            cv = cv.named('foo')
        do_naming = lambda obj, obj_type, store_name: cv.named('foo')
        assert cv.is_named == named
        self.wizard.name = mock.Mock(side_effect=do_naming)
        assert len(self.wizard.cvs) == 0
        self.wizard.register(cv, 'CV', 'cvs')
        assert len(self.wizard.cvs) == 1
        assert cv.name == 'foo'

    def _get_storage(self, inputs, expected):
        console = MockConsole(inputs)
        self.wizard.console = console
        storage = self.wizard.get_storage()
        assert storage.backend.filename == expected
        assert console.input_call_count == len(inputs)

    @pytest.mark.parametrize('fnames', [(['setup.db']),
                                        (['setup.nc', 'setup.db'])])
    def test_get_storage(self, tmpdir, fnames):
        inputs = [os.path.join(tmpdir, inp) for inp in fnames]
        self._get_storage(inputs, inputs[-1])

    @pytest.mark.parametrize('overwrite', [True, False])
    def test_get_storage_exists(self, overwrite, tmpdir):
        inputs = [os.path.join(tmpdir, 'setup.db'),
                  {True: 'y', False: 'n'}[overwrite]]
        if not overwrite:
            inputs.append(os.path.join(tmpdir, 'setup2.db'))

        pathlib.Path(inputs[0]).touch()
        expected = 'setup.db' if overwrite else 'setup2.db'
        self._get_storage(inputs, os.path.join(tmpdir, expected))

    def test_get_storage_file_error(self, tmpdir):
        inputs = ['/oogabooga/foo/bar.db', os.path.join(tmpdir, 'setup.db')]
        self._get_storage(inputs, inputs[-1])

    @pytest.mark.parametrize('count', [0, 1, 2])
    def test_storage_description_line(self, count):
        from openpathsampling.experimental.storage.collective_variables \
                import CoordinateFunctionCV
        expected = {0: "",
                    1: "* 1 cv: ['foo']",
                    2: "* 2 cvs: ['foo', 'bar']"}[count]

        self.wizard.cvs = {
            name: CoordinateFunctionCV(lambda s: s.xyz[0][0]).named(name)
            for name in ['foo', 'bar'][:count]
        }
        line = self.wizard._storage_description_line('cvs')
        assert line == expected

    def test_save_to_file(self, toy_engine):
        console = MockConsole([])
        self.wizard.console = console
        self.wizard.register(toy_engine, 'Engine', 'engines')
        storage = MockStorage()
        self.wizard.save_to_file(storage)
        assert len(storage.cvs) == len(storage.volumes) == 0
        assert len(storage.networks) == len(storage.schemes) == 0
        assert len(storage.engines) == 1
        assert storage.engines[toy_engine.name] == toy_engine
        assert storage.engines[0] == toy_engine
        assert "Everything has been stored" in self.wizard.console.log_text

    @pytest.mark.parametrize('req,count,expected', [
        (('cvs', 1, 1), 0, (True, True)),
        (('cvs', 1, 1), 1, (False, False)),
        (('cvs', 1, 2), 1, (False, True)),
        ((None, 0, 0), 0, (True, False))
    ])
    def test_req_do_another(self, req, count, expected):
        self.wizard.cvs = {str(i): 'foo' for i in range(count)}
        assert self.wizard._req_do_another(req) == expected

    @pytest.mark.parametrize('inputs,expected', [
        (['y'], True), (['z', 'y'], True), (['z', 'n'], False),
        (['n'], False)
    ])
    def test_ask_do_another(self, inputs, expected):
        console = MockConsole(inputs)
        self.wizard.console = console
        result = self.wizard._ask_do_another("CV")
        assert result == expected
        assert "another CV" in console.log_text
        if len(inputs) > 1:
            assert "Sorry" in console.log_text

    @pytest.mark.parametrize('min_max,do_another', [
        ((1, 1), False), ((2, float('inf')), True), ((1, 2), 'asked')
    ])
    def test_do_one(self, toy_engine, min_max, do_another):
        step = mock.Mock(
            func=mock.Mock(return_value=toy_engine),
            display_name='Engine',
            store_name='engines'
        )
        req = ('engines', *min_max)
        # mock user interaction with response 'asked'
        with mock.patch.object(Wizard, '_ask_do_another',
                               return_value='asked'):
            result = self.wizard._do_one(step, req)

        assert result == do_another
        assert self.wizard.engines[toy_engine.name] == toy_engine

    def test_do_one_restart(self):
        step = mock.Mock(
            func=mock.Mock(side_effect=RestartObjectException()),
            display_name='Engine', store_name='engines'
        )
        req = ('engines', 1, 1)
        result = self.wizard._do_one(step, req)
        assert result is True
        assert len(self.wizard.engines) == 0

    def test_run_wizard(self, toy_engine):
        # skip patching the wizard; we never actually use the saving
        # mechanisms and don't want to unpatch after
        self.wizard._patched = True
        step = mock.Mock(
            func=mock.Mock(return_value=toy_engine),
            display_name='Engine',
            store_name='engines',
            minimum=1,
            maximum=1
        )
        self.wizard.steps = [step]
        storage = MockStorage()
        with mock.patch.object(Wizard, 'get_storage',
                               mock.Mock(return_value=storage)):
            self.wizard.run_wizard()
        assert len(storage.cvs) == len(storage.volumes) == 0
        assert len(storage.networks) == len(storage.schemes) == 0
        assert len(storage.engines) == 1
        assert storage.engines[toy_engine.name] == toy_engine
        assert storage.engines[0] == toy_engine

    def test_run_wizard_quit(self):
        console = MockConsole()
        self.wizard.console = console
        self.wizard._patched = True
        step = mock.Mock(
            func=mock.Mock(side_effect=QuitWizard()),
            display_name='Engine',
            store_name='engines',
            minimum=1,
            maximum=1
        )
        self.wizard.steps = [step]
        mock_ask_save = mock.Mock(return_value=False)
        with mock.patch.object(Wizard, '_ask_save', mock_ask_save):
            self.wizard.run_wizard()
        assert "Goodbye!" in self.wizard.console.log_text

    @pytest.mark.parametrize('inputs', ['y', 'n'])
    def test_ask_save(self, inputs):
        expected = {'y': True, 'n': False}[inputs]
        console = MockConsole(['foo', inputs])
        self.wizard.console = console
        result = self.wizard._ask_save()
        assert result is expected
        assert "Before quitting" in self.wizard.console.log_text
        assert "Sorry" in self.wizard.console.log_text


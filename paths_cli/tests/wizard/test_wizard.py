import pytest
import mock
from paths_cli.tests.wizard.mock_wizard import (
    MockConsole, make_mock_wizard, make_mock_retry_wizard
)
import pathlib

from openpathsampling.experimental.storage.collective_variables import \
        CoordinateFunctionCV

from paths_cli.wizard.wizard import *
from paths_cli.wizard.steps import SINGLE_ENGINE_STEP



class TestWizard:
    def setup(self):
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
        pass

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

    def test_save_to_file(self):
        pass

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

    def test_run_wizard(self):
        pass

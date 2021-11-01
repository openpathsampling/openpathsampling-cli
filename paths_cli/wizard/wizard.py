import random
import os
from functools import partial
import textwrap

from paths_cli.wizard.tools import yes_no, a_an
from paths_cli.wizard.core import get_object
from paths_cli.wizard.errors import (
    FILE_LOADING_ERROR_MSG, RestartObjectException
)
from paths_cli.wizard.joke import name_joke
from paths_cli.wizard.helper import Helper, QuitWizard
from paths_cli.compiling.tools import custom_eval

import shutil

class Console:  # no-cov
    # TODO: add logging so we can output the session
    def print(self, *content):
        print(*content)

    def input(self, content):
        return input(content)

    @property
    def width(self):
        return shutil.get_terminal_size((80, 24)).columns

class Wizard:
    def __init__(self, steps):
        self.steps = steps
        self.requirements = {
            step.display_name: (step.store_name, step.minimum, step.maximum)
            for step in steps
        }
        self.engines = {}
        self.cvs = {}
        self.states = {}
        self.networks = {}
        self.schemes = {}

        self.last_used_file = None  # for loading

        self.console = Console()
        self.default = {}
        self._patched = False  # if we've done the monkey-patching

    def _patch(self):  # no-cov
        import openpathsampling as paths
        from openpathsampling.experimental.storage import monkey_patch_all
        from paths_cli.param_core import StorageLoader
        if not self._patched:
            paths = monkey_patch_all(paths)
            paths.InterfaceSet.simstore = True
            self._patched = True
            StorageLoader.has_simstore_patch = True

    def debug(content):  # no-cov
        # debug does no pretty-printing
        self.console.print(content)

    def _speak(self, content, preface):
        # we do custom wrapping here
        # TODO: move this to the console class; should also wrap on `input`
        width = self.console.width - len(preface)
        statement = preface + content
        lines = statement.split("\n")
        wrapped = textwrap.wrap(lines[0], width=width, subsequent_indent=" "*3)
        for line in lines[1:]:
            if line == "":
                wrapped.append("")
                continue
            wrap_line = textwrap.wrap(line, width=width,
                                      initial_indent=" "*3,
                                      subsequent_indent=" "*3)
            wrapped.extend(wrap_line)
        self.console.print("\n".join(wrapped))

    @get_object
    def ask(self, question, options=None, default=None, helper=None,
            autohelp=False):
        if helper is None:
            helper = Helper(None)
        if isinstance(helper, str):
            helper = Helper(helper)
        result = self.console.input("🧙 " + question + " ")
        self.console.print()
        if helper and result[0] in ["?", "!"]:
            self.say(helper(result))
            return
        return result

    def say(self, content, preface="🧙 "):
        self._speak(content, preface)
        self.console.print()  # adds a blank line

    def start(self, content):
        # eventually, this will tweak so that we preface with a line and use
        # green text here
        self.say(content)

    def bad_input(self, content, preface="👺 "):
        # just changes the default preface; maybe print 1st line red?
        self.say(content, preface)

    @get_object
    def ask_enumerate_dict(self, question, options, helper=None,
                           autohelp=False):
        self.say(question)
        opt_string = "\n".join([f" {(i+1):>3}. {opt}"
                                for i, opt in enumerate(options)])
        self.say(opt_string, preface=" "*3)
        choice = self.ask("Please select an option:", helper=helper)

        # select by string
        if choice in options:
            return options[choice]

        # select by number
        try:
            num = int(choice) - 1
            result = list(options.values())[num]
        except Exception:
            self.bad_input(f"Sorry, '{choice}' is not a valid option.")
            result = None

        return result

    def ask_enumerate(self, question, options):
        """Ask the user to select from a list of options"""
        self.say(question)
        opt_string = "\n".join([f" {(i+1):>3}. {opt}"
                                for i, opt in enumerate(options)])
        self.say(opt_string, preface=" "*3)
        result = None
        while result is None:
            choice = self.ask("Please select a number:",
                              options=[str(i+1)
                                       for i in range(len(options))])
            if choice in options:
                return choice

            try:
                num = int(choice) - 1
                result = options[num]
            except Exception:
                self.bad_input(f"Sorry, '{choice}' is not a valid option.")
                result = None

        return result

    @get_object
    def ask_load(self, question, loader, helper=None, autohelp=False):
        as_str = self.ask(question, helper=helper)
        try:
            result = loader(as_str)
        except Exception as e:
            self.exception(f"Sorry, I couldn't understand the input "
                           f"'{as_str}'.", e)
            return
        return result

    # this should match the args for wizard.ask
    @get_object
    def ask_custom_eval(self, question, options=None, default=None,
                        helper=None, type_=float):
        as_str = self.ask(question, options=options, default=default,
                          helper=helper)
        try:
            result = type_(custom_eval(as_str))
        except Exception as e:
            self.exception(f"Sorry, I couldn't understand the input "
                           f"'{as_str}'", e)
            return
        return result


    def obj_selector(self, store_name, text_name, create_func):
        opts = {name: lambda wiz, o=obj: o
                for name, obj in getattr(self, store_name).items()}
        create_new = f"Create a new {text_name}"
        opts[create_new] = create_func
        sel = self.ask_enumerate(f"Which {text_name} would you like to "
                                 "use?", list(opts.keys()))
        obj = opts[sel](self)
        if sel == create_new:
            obj = self.register(obj, text_name, store_name)
        return obj

    def exception(self, msg, exception):
        self.bad_input(f"{msg}\nHere's the error I got:\n"
                       f"{exception.__class__.__name__}: {exception}")

    def name(self, obj, obj_type, store_name, default=None):
        self.say(f"Now let's name your {obj_type}.")
        name = None
        while name is None:
            name_help = ("Objects in OpenPathSampling can be named. You'll "
                         "use these names to refer back to these objects "
                         "or to load them from a storage file.")
            name = self.ask("What do you want to call it?", helper=name_help)
            if name in getattr(self, store_name):
                self.bad_input(f"Sorry, you already have {a_an(obj_type)} "
                               f"named {name}. Please try another name.")
                name = None

        obj = obj.named(name)

        self.say(f"'{name}' is a good name for {a_an(obj_type)} {obj_type}. "
                 + name_joke(name, obj_type))
        return obj


    def register(self, obj, obj_type, store_name):
        if not obj.is_named:
            obj = self.name(obj, obj_type, store_name)
        store_dict = getattr(self, store_name)
        store_dict[obj.name] = obj
        return obj

    @get_object
    def get_storage(self):
        from openpathsampling.experimental.storage import Storage
        filename = self.ask("Where would you like to save your setup "
                            "database?")
        if not filename.endswith(".db"):
            self.bad_input("Files produced by this wizard must end in "
                           "'.db'.")
            return

        if os.path.exists(filename):
            overwrite = self.ask(f"{filename} exists. Overwrite it?",
                                 options=["[Y]es", "[N]o"])
            overwrite = yes_no(overwrite)
            if not overwrite:
                return

        try:
            storage = Storage(filename, mode='w')
        except Exception as e:
            self.exception(FILE_LOADING_ERROR_MSG, e)
            return

        return storage


    def _storage_description_line(self, store_name):
        store = getattr(self, store_name)
        if len(store) == 0:
            return ""

        if len(store) == 1:
            store_name = store_name[:-1]  # chop the 's'

        line = f"* {len(store)} {store_name}: " + str(list(store.keys()))
        return line

    def save_to_file(self, storage):
        store_names = ['engines', 'cvs', 'states', 'networks', 'schemes']
        lines = [self._storage_description_line(store_name)
                 for store_name in store_names]
        statement = ("I'm going to store the following items:\n\n"
                     + "\n".join([line for line in lines if len(line) > 0]))
        self.say(statement)
        for store_name in store_names:
            store = getattr(self, store_name)
            for obj in store.values():
                storage.save(obj)

        self.say("Success! Everything has been stored in your file.")

    def _req_do_another(self, req):
        store, min_, max_ = req
        if store is None:
            return (True, False)

        count = len(getattr(self, store))
        allows = count < max_
        requires = count < min_
        return requires, allows

    def _ask_do_another(self, obj_type):
        do_another = None
        while do_another is None:
            do_another_char = self.ask(
                f"Would you like to make another {obj_type}?",
                options=["[Y]es", "[N]o"]
            )
            try:
                do_another = yes_no(do_another_char)
            except KeyError:
                self.bad_input("Sorry, I didn't understand that.")
        return do_another

    def _do_one(self, step, req):
        try:
            obj = step.func(self)
        except RestartObjectException:
            self.say("Okay, let's try that again.")
            return True
        self.register(obj, step.display_name, step.store_name)
        requires_another, allows_another = self._req_do_another(req)
        if requires_another:
            do_another = True
        elif not requires_another and allows_another:
            do_another = self._ask_do_another(step.display_name)
        else:
            do_another = False
        return do_another

    def run_wizard(self):
        self.start("Hi! I'm the OpenPathSampling Wizard.")
        # TODO: next line is only temporary
        self.say("Today I'll help you set up a 2-state TPS simulation.")
        self._patch()  # try to hide the slowness of our first import
        try:
            for step in self.steps:
                req = step.store_name, step.minimum, step.maximum
                do_another = True
                while do_another:
                    do_another = self._do_one(step, req)
        except QuitWizard:
            do_save = self._ask_save()
        else:
            do_save = True

        if do_save:
            storage = self.get_storage()
            self.save_to_file(storage)
        else:
            self.say("Goodbye! 👋")

    @get_object
    def _ask_save(self):
        do_save_char = self.ask("Before quitting, would you like to save "
                                "the objects you've created so far?")
        try:
            do_save = yes_no(do_save_char)
        except Exception:
            self.bad_input("Sorry, I didn't understance that.")
            return None
        return do_save


# FIXED_LENGTH_TPS_WIZARD
# MULTIPLE_STATE_TPS_WIZARD
# TWO_STATE_TIS_WIZARD
# MULTIPLE_STATE_TIS_WIZARD
# MULTIPLE_INTERFACE_SET_TIS_WIZARD

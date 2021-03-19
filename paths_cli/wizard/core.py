import random
from paths_cli.wizard.joke import name_joke
from paths_cli.wizard.tools import a_an

from collections import namedtuple

WizardSay = namedtuple("WizardSay", ['msg', 'mode'])

def interpret_req(req):
    _, min_, max_ = req
    string = ""
    if min_ == max_:
        return str(min_)

    if min_ >= 1:
        string += "at least " + str(min_)

    if max_ < float("inf"):
        if string != "":
            string += " and "
        string += "at most " + str(max_)

    return string


def get_missing_object(wizard, obj_dict, display_name, fallback_func):
    if len(obj_dict) == 0:
        obj = fallback_func(wizard)
    elif len(obj_dict) == 1:
        obj = list(obj_dict.values())[0]
    else:
        objs = list(obj_dict.keys())
        sel = wizard.ask_enumerate(f"Which {display_name} would you like "
                                   "to use?", options=objs)
        obj = obj_dict[sel]
    return obj


def get_object(func):
    def inner(*args, **kwargs):
        obj = None
        while obj is None:
            obj = func(*args, **kwargs)
        return obj
    return inner



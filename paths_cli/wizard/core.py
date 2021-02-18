import random
from joke import name_joke
from tools import a_an

def name(wizard, obj, obj_type, store_name, default=None):
    wizard.say(f"Now let's name your {obj_type}.")
    name = None
    while name is None:
        name = wizard.ask("What do you want to call it?")
        if name in getattr(wizard, store_name):
            wizard.bad_input(f"Sorry, you already have {a_an(obj_type)} "
                             f"named {name}. Please try another name.")
            name = None

    obj = obj.named(name)

    wizard.say(f"'{name}' is a good name for {a_an(obj_type)} {obj_type}. "
               + name_joke(name, obj_type))
    return obj

def abort_retry_quit(wizard, obj_type):
    a_an = 'an' if obj_type[0] in 'aeiou' else 'a'
    retry = wizard.ask(f"Do you want to try again to make {a_an} "
                       f"{obj_type}, do you want to continue without, or "
                       f"do you want to quit?",
                       options=["[R]etry", "[C]ontinue", "[Q]uit"])
    if retry == 'q':
        exit()
    elif retry == 'r':
        return
    elif retry == 'c':
        return "continue"
    else:
        raise ImpossibleError()


def interpret_req(req):
    _, num, direction = req
    dir_str = {'+': 'at least ', '=': '', '-': 'at most '}[direction]
    return dir_str + str(num)


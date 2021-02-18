import random

from paths_cli.wizard.tools import a_an

_NAMES = ['Fred', 'Winston', 'Agnes', "Millicent", "Ophelia", "Laszlo",
          "Werner"]
_THINGS = ['pet spider', 'teddy bear', 'close friend', 'school teacher',
           'iguana']
_SPAWN = ['daughter', 'son', 'first-born']

_MISC = [
    "Named after its father, perhaps?",
    "Isn't '{name}' also the name of a village in Tuscany?",
    "Didn't Johnny Cash write a song about {a_an_thing} called '{name}'?",
    "I think I'm going to start rapping as 'DJ {name}'.",
]

def _joke1(name, obj_type):
    return (f"I probably would have named it something like "
            f"'{random.choice(_NAMES)}'.")

def _joke2(name, obj_type):
    thing = random.choice(_THINGS)
    joke = (f"I had {a_an(thing)} {thing} named '{name}' "
            f"when I was young.")
    return joke

def _joke3(name, obj_type):
    return (f"I wanted to name my {random.choice(_SPAWN)} '{name}', but my "
            f"wife wouldn't let me.")

def _joke4(name, obj_type):
    a_an_thing = a_an(obj_type) + f" {obj_type}"
    return random.choice(_MISC).format(name=name, obj_type=obj_type,
                                       a_an_thing=a_an_thing)

def name_joke(name, obj_type):
    rnd = random.random()
    if 0 <= rnd < 0.30:
        joke = _joke1
    elif 0.30 <= rnd < 0.70:
        joke = _joke2
    elif 0.70 <= rnd < 0.85:
        joke = _joke4
    else:
        joke = _joke3
    return joke(name, obj_type)

if __name__ == "__main__":
    for _ in range(5):
        print()
        print(name_joke('AD_300K', 'engine'))
        print()
        print(name_joke('C_7eq', 'state'))

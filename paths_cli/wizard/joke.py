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
    "Didn't Johnny Cash write a song about {a_an_thing} named '{name}'?",
    "I think I'm going to start rapping as 'DJ {name}'.",
    "It would also be a good name for a death metal band.",
]


def _joke1(name, obj_type):  # no-cov
    return (f"I probably would have named it something like "
            f"'{random.choice(_NAMES)}'.")


def _joke2(name, obj_type):  # no-cov
    thing = random.choice(_THINGS)
    joke = (f"I had {a_an(thing)} {thing} named '{name}' "
            f"when I was young.")
    return joke


def _joke3(name, obj_type):  # no-cov
    return (f"I wanted to name my {random.choice(_SPAWN)} '{name}', but my "
            f"wife wouldn't let me.")


def _joke4(name, obj_type):  # no-cov
    a_an_thing = a_an(obj_type) + f" {obj_type}"
    return random.choice(_MISC).format(name=name, obj_type=obj_type,
                                       a_an_thing=a_an_thing)


def name_joke(name, obj_type):  # no-cov
    """Make a joke about the naming process."""
    jokes = [_joke1, _joke2, _joke3, _joke4]
    weights = [5, 5, 3, 7]
    joke = random.choices(jokes, weights=weights)[0]
    return joke(name, obj_type)


if __name__ == "__main__":  # no-cov
    for _ in range(5):
        print()
        print(name_joke('AD_300K', 'engine'))
        print()
        print(name_joke('C_7eq', 'state'))

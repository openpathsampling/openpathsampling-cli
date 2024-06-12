def a_an(obj):
    return "an" if obj[0].lower() in "aeiou" else "a"


def yes_no(char):
    return {'yes': True, 'no': False, 'y': True, 'n': False}[char.lower()]

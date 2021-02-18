
def a_an(obj):
    return "an" if obj[0] in "aeiou" else "a"

def yes_no(char):
    return {'y': True, 'n': False}[char]

def get_int_value(wizard, question, default=None, helper=None):
    as_int = None
    while as_int is None:
        evald = wizard.ask_custom_eval(question, default=default,
                                       helper=helper)
        try:
            as_int = int(evald)
        except Exception as e:
            wizard.exception("Sorry, I didn't understand that.", e)
    return as_int

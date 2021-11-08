
def json_type_ref(category):
    return {"$ref": f"#/definitions/{category}_type"}

def json_type_eval(check_type):
    return {"$ref": f"#/definitions/Eval{check_type}"}

def json_type_list(item_type):
    return {'type': 'array',
            'items': item_type}

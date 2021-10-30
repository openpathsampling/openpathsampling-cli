class JsonTypeHandler:
    def __init__(self, is_my_type, handler):
        self._is_my_type = is_my_type
        self.handler = handler

    def is_my_type(self, json_type):
        return self._is_my_type(json_type)

    def __call__(self, json_type):
        if self.is_my_type(json_type):
            return self.handler(json_type)
        return json_type


handle_object = JsonTypeHandler(
    is_my_type=lambda json_type: json_type == "object",
    handler=lambda json_type: "dict",
)


def _is_listof(json_type):
    try:
        return json_type["type"] == "array"
    except:
        return False


handle_listof = JsonTypeHandler(
    is_my_type=_is_listof,
    handler=lambda json_type: "list of "
    + json_type_to_string(json_type["items"]),
)


class RefTypeHandler(JsonTypeHandler):
    def __init__(self, type_name, def_string, link_to):
        self.type_name = type_name
        self.def_string = def_string
        self.link_to = link_to
        self.json_check = {"$ref": "#/definitions/" + def_string}
        super().__init__(is_my_type=self._reftype, handler=self._refhandler)

    def _reftype(self, json_type):
        return json_type == self.json_check

    def _refhandler(self, json_type):
        rst = f"{self.type_name}"
        if self.link_to:
            rst = f":ref:`{rst} <{self.link_to}>`"
        return rst


class CategoryHandler(RefTypeHandler):
    def __init__(self, category):
        self.category = category
        def_string = f"{category}_type"
        link_to = f"compiling--{category}"
        super().__init__(
            type_name=category, def_string=def_string, link_to=link_to
        )


class EvalHandler(RefTypeHandler):
    def __init__(self, type_name, link_to=None):
        super().__init__(
            type_name=type_name, def_string=type_name, link_to=link_to
        )


JSON_TYPE_HANDLERS = [
    handle_object,
    handle_listof,
    CategoryHandler("engine"),
    CategoryHandler("cv"),
    CategoryHandler("volume"),
    EvalHandler("EvalInt"),
    EvalHandler("EvalFloat"),
]


def json_type_to_string(json_type):
    for handler in JSON_TYPE_HANDLERS:
        handled = handler(json_type)
        if handled != json_type:
            return handled
    return json_type

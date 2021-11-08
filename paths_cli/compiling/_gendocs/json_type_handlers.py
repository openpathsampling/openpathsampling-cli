class JsonTypeHandler:
    """Abstract class to obtain documentation type from JSON schema type.

    Parameters
    ----------
    is_my_type : Callable[Any] -> bool
        return True if this instance should handle the given input type
    handler : Callable[Any] -> str
        convert the input type to a string suitable for the RST docs
    """
    def __init__(self, is_my_type, handler):
        self._is_my_type = is_my_type
        self.handler = handler

    def is_my_type(self, json_type):
        """Determine whether this instance should handle this type.

        Parameters
        ----------
        json_type : Any
            input type from JSON schema

        Returns
        -------
        bool :
            whether to handle this type with this instance
        """
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
    except:  # any exception should return false (mostly Key/Type Error)
        return False


handle_listof = JsonTypeHandler(
    is_my_type=_is_listof,
    handler=lambda json_type: "list of "
    + json_type_to_string(json_type["items"]),
)


handle_none = JsonTypeHandler(
    is_my_type=lambda obj: obj is None,
    handler=lambda json_type: "type information missing",
)


class RefTypeHandler(JsonTypeHandler):
    """Handle JSON types of the form {"$ref": "#/definitions/..."}

    Parameters
    ----------
    type_name : str
        the name to use in the RST type
    def_string : str
        the string following "#/definitions/" in the JSON type definition
    link_to : str or None
        if not None, the RST type will be linked with a ``:ref:`` pointing
        to the anchor given by ``link_to``
    """
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
    """Handle JSON types for OPS category definitions.

    OPS category definitions show up with JSON references pointing to
    "#/definitions/{CATEGORY}_type". This provides a convenience class over
    the :class:RefTypeHandler to treat OPS categories.

    Parameters
    ----------
    category : str
        name of the category
    """
    def __init__(self, category):
        self.category = category
        def_string = f"{category}_type"
        link_to = f"compiling--{category}"
        super().__init__(
            type_name=category, def_string=def_string, link_to=link_to
        )


class EvalHandler(RefTypeHandler):
    """Handle JSON types for OPS custom evaluation definitions.

    Some parameters for the OPS compiler use the OPS custom evaluation
    mechanism, which evaluates certain Python-like string input. These are
    treated as special definition types in the JSON schema, and this object
    provides a convenience class over :class:`.RefTypeHandler` to treat
    custom evaluation types.

    Parameters
    ----------
    type_name : str
        name of the custom evaluation type
    link_to : str or None
        if not None, the RST type will be linked with a ``:ref:`` pointing
        to the anchor given by ``link_to``
    """
    def __init__(self, type_name, link_to=None):
        if link_to is None:
            link_to = type_name

        super().__init__(
            type_name=type_name, def_string=type_name, link_to=link_to
        )


JSON_TYPE_HANDLERS = [
    handle_object,
    handle_none,
    handle_listof,
    CategoryHandler("engine"),
    CategoryHandler("cv"),
    CategoryHandler("volume"),
    CategoryHandler("network"),
    CategoryHandler("strategy"),
    CategoryHandler("scheme"),
    CategoryHandler("shooting-point-selector"),
    CategoryHandler("interface-set"),
    EvalHandler("EvalInt"),
    EvalHandler("EvalIntStrictPos"),
    EvalHandler("EvalFloat"),
]


def json_type_to_string(json_type):
    """Convert JSON schema type to string for RST docs.

    This is the primary public-facing method for dealing with JSON schema
    types in RST document generation.

    Parameters
    ----------
    json_type : Any
        the type from the JSON schema

    Returns
    -------
    str :
        the type string description to be used in the RST document
    """
    for handler in JSON_TYPE_HANDLERS:
        handled = handler(json_type)
        if handled != json_type:
            return handled
    return json_type

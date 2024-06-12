import pytest

from paths_cli.compiling._gendocs.json_type_handlers import *


@pytest.mark.parametrize('json_type', ['object', 'foo'])
def test_handle_object(json_type):
    # object should convert to dict; anything else should be is-identical
    if json_type == "foo":
        json_type = {'foo': 'bar'}  # make the `is` test meaningful
    result = handle_object(json_type)
    if json_type == 'object':
        assert result == 'dict'
    else:
        assert result is json_type


def test_handle_listof():
    json_type = {'type': "array", "items": "float"}
    assert handle_listof(json_type) == "list of float"


def test_category_handler():
    json_type = {"$ref": "#/definitions/engine_type"}
    handler = CategoryHandler('engine')
    assert handler(json_type) == ":ref:`engine <compiling--engine>`"


def test_eval_handler():
    json_type = {"$ref": "#/definitions/EvalInt"}
    handler = EvalHandler("EvalInt", link_to="EvalInt")
    assert handler(json_type) == ":ref:`EvalInt <EvalInt>`"


@pytest.mark.parametrize('json_type', ['string', 'float', 'list-float',
                                       'engine', 'list-engine'])
def test_json_type_to_string(json_type):
    # integration tests for json_type_to_string
    inputs, expected = {
        'string': ("string", "string"),
        'float': ("float", "float"),
        'list-float': ({'type': 'array', 'items': 'float'},
                       "list of float"),
        'engine': ({"$ref": "#/definitions/engine_type"},
                   ":ref:`engine <compiling--engine>`"),
        'list-engine': ({"type": "array",
                         "items": {"$ref": "#/definitions/engine_type"}},
                        "list of :ref:`engine <compiling--engine>`"),
    }[json_type]
    assert json_type_to_string(inputs) == expected

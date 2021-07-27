import pytest
from unittest import mock

from paths_cli.wizard.tools import *

@pytest.mark.parametrize('word,expected', [
    ('foo', 'a'), ('egg', 'an')
])
def test_a_an(word, expected):
    assert a_an(word) == expected


@pytest.mark.parametrize('user_inp,expected', [
    ('y', True), ('n', False),
    ('Y', True), ('N', False), ('yes', True), ('no', False)
])
def test_yes_no(user_inp, expected):
    assert yes_no(user_inp) == expected

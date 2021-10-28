import pytest
from paths_cli.wizard.standard_categories import *

def test_get_category_info():
    cat = get_category_info('cv')
    assert cat.name == 'cv'
    assert cat.singular == 'CV'
    assert cat.plural == "CVs"
    assert cat.storage == "cvs"

def test_get_category_info_error():
    with pytest.raises(RuntimeError, match="No category"):
        get_category_info("foo")

import pytest
from unittest import mock

from paths_cli.compiling._gendocs.config_handler import *

GOOD_DATA = {'engine': {'header': "Engines", 'description': "desc"}}

MODULE_LOC = "paths_cli.compiling._gendocs.config_handler."


def test_load_config():
    # load_config should create the correct DocCategoryInfo objects
    mock_open = mock.mock_open(read_data="unused")
    mock_loader = mock.Mock(return_value=mock.Mock(return_value=GOOD_DATA))
    with mock.patch(MODULE_LOC + "open", mock_open) as m_open, \
            mock.patch(MODULE_LOC + "select_loader", mock_loader) as m_load:
        config = load_config("foo.yml")
    assert 'engine' in config
    data = config['engine']
    assert isinstance(data, DocCategoryInfo)
    assert data.header == "Engines"
    assert data.description == "desc"


def test_load_config_file_error():
    # if the filename is bad, we should get a FileNotFoundError
    with pytest.raises(FileNotFoundError):
        load_config("foo.yml")


def test_load_config_data_error():
    # if the data can't be mapped to a DocCategoryInfo class, we should get
    # a TypeError
    BAD_DATA = {'engine': {'foo': 'bar'}}
    mock_open = mock.mock_open(read_data="unused")
    mock_loader = mock.Mock(return_value=mock.Mock(return_value=BAD_DATA))
    with mock.patch(MODULE_LOC + "open", mock_open) as m_open, \
            mock.patch(MODULE_LOC + "select_loader", mock_loader) as m_load:
        with pytest.raises(TypeError, match='unexpected keyword'):
            load_config("foo.yml")

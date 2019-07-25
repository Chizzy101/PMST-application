import pytest
import pmst

# Create Query object for testing
qt = pmst.Query()

# Tests for the Query class
def test_query_geom_dict():
    assert type(pmst.Query._GEOM_TYPE_DICT) is dict, "Class variable _GEOM_TYPE_DICT is not a dictionary"

def test_query_coord_dict():
    assert type(pmst.Query._COORD_TYPE_DICT) is dict, "Class variable _COORD_TYPE_DICT is not a dictionary"

def test_query_set_coord_type():
    with pytest.raises(Exception):
        assert qt.set_coord_type(coord_type=42)
import pytest
import pmst
from bs4 import BeautifulSoup
import os

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

# test the get_tec() method selects the correct threatened categories

# test set up - create test class that over-rides the _get_html() method to use the test html files
class TestTec(pmst.Tec):
    """Test class used to make TEC for testing only. Inherits from the TEC
    class in pmst.py.
    """
    def __init__(self, url):
        self._set_url(url)
        self._get_html()
        self.set_cat()
        self.get_name()

    def _set_url(self, url):
        """Custom test method to create the URL for test set-up.
        
        Arguments:
            url {str} -- URL in string format to the .html file in the test
            suite
        """
        self.url = os.path.abspath(url)

    def _get_html(self):
        """Custom test method to create class html attribute from the test
        .html files. Over-rides the superclass _get_html() method.
        """
        self._soup = BeautifulSoup(open(self.url), "lxml")
        print(r"Test Protected Matter added to object {0}".format(self.url))

# set up code - create the test TECs
tec_crit = TestTec(".\\tests\\html\\tec_crit_end.html")
tec_end = TestTec(".\\tests\\html\\tec_end.html")
tec_vul = TestTec(".\\tests\\html\\tec_vul.html")


def test_tec_find_category_crit_end():
    """Tests that a critically endangered TEC doesn't get classified as an
    endangered or vulnerable TEC. Uses .html file in .\\tests\\html
    """
    assert tec_crit.category == 'Critically Endangered'
    with pytest.raises(Exception):
        assert tec_crit.category == 'Endangered'
    with pytest.raises(Exception):
        assert tec_crit.category == 'Vulnerable'


def test_tec_find_category_end():
    """Tests that an endangered TEC doesn't get classified as an critically
    endangered or vulnerable TEC. Uses .html file in .\\tests\\html
    """
    assert tec_end.category == 'Endangered'
    with pytest.raises(Exception):
        assert tec_end.category == 'Critically Endangered'
    with pytest.raises(Exception):
        assert tec_end.category == 'Vulnerable'


def test_tec_find_category_vul():
    """Tests that a vulnerable TEC doesn't get classified as a critically
    endangered or vulnerable TEC. Uses .html file in .\\tests\\html
    """
    assert tec_vul.category == 'Vulnerable'
    with pytest.raises(Exception):
        assert tec_vul.category == 'Critically Endangered'
    with pytest.raises(Exception):
        assert tec_vul.category == 'Endangered'

def test_tec_cat_list():
    assert type(pmst.Tec.TEC_CAT_LIST) is list, "TEC_CAT_LIST type is not list"

def test_tec_get_name():
    assert tec_crit.name == 'Thrombolite (microbialite) Community of a Coastal Brackish Lake (Lake Clifton)'
    assert tec_end.name == 'Aquatic Root Mat Community 1 in Caves of the Leeuwin Naturaliste Ridge'
    assert tec_vul.name == 'Subtropical and Temperate Coastal Saltmarsh'
    

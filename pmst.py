"""Contains classes for PMST objects
"""

from bs4 import BeautifulSoup
import datetime
import re
import requests


class Query():
    """PMST report object. Can be used to create a new query - look at using
    Selenium.
    Can be created from an existing PMST report object
    """

    """To Do List
    Add a check for geometry set method - if more than one point in the coords
    list then the geom can't be point
    Add a check for the set coord list method to check against the geometry
    type. Of there's more than one set of points then it can't be a point geom.
    The number of points in the coord list must be <= 150, add check for this.
    """

    _GEOM_TYPE_DICT = {
        1: "Point",
        2: "Line",
        3: "Polygon",
        4: "Undefined",
    }

    _COORD_TYPE_DICT = {
        1: "Decimal degrees",
        2: "Degrees minutes seconds",
        3: "Undefined",
    }

    def __init__(self, file, **kwargs):
        self.name = None
        self.coord_type = kwargs.get('coord_type', 3)
        self.coord_list = None
        self.geom_type = None
        self.buffer = kwargs.get('buffer', 1)
        self.email = kwargs.get('email', None)

        # this doesn't seem very Pythonic, might be a better way to implement
        # this
        if 'geom_type' in kwargs:
            self.set_geom_type(kwargs.get('geom_type'))
        else:
            self.geom_type = 4

    def set_geom_type(self, geom_type):
        """Sets the geometry type of the query (point, line, area). This can't
        be derived from PMST report except for the cases where there is one
        coordinate pair (geometry must be a point) or two coordinate pairs
        (geometry must be a line). Any case where three or more pairs of
        coordinates occur could be either a line or an area. Any case with two
        or more pairs of coordinates can't be a point.
        """
        if geom_type in self._GEOM_TYPE_DICT:
            self.geom_type = geom_type
        else:
            raise ValueError('geom_type out of range')

    def set_coord_type(self, coord_type):
        if coord_type in self._COORD_TYPE_DICT:
            self.coord_type = coord_type
        else:
            raise ValueError('coord_type out of range')

    def set_coord_list(self, coord_list):

        def _check_coord_pair(coords):
            """Coords must be a pair. Lat must be in first position of coords pair
            and must be between -70 and -5. Long must be in second position and
            must be between 65 and 180
            """

            if len(coords) != 2:
                raise ValueError('Coordinates must be a pair of numbers')

            if not -70 < coords[0] < -5:
                raise ValueError('Latitude out of range')

            if not 65 < coords[1] < 180:
                raise ValueError('Longitude out of range')

            return True

        def _trim_coord_pair(coords):
            """Trims coords to 5 places if the coord is a long float
            Not yet implemented
            """
            pass

        if len(coord_list) < 150:
            raise ValueError('coord_list must be <= 150')

        coord_list = []

        for coords in coord_list:
            if _check_coord_pair(coords):
                coord_list.append(coords)

        self.coord_list = coord_list

    def set_buffer(self, buffer):
        """To do
        """
        try:
            buffer_string = self.soup.find(
                        "span", text=re.compile(r'(Buffer:)')
                    ).text
        except:
            print("No buffer found")

        def find_buffer(string):
            try:
                result = re.search(r"[-+]?\d*\.\d+|\d+", string)
                return result.group()
            except:
                print("No date found")

        try:
            self.buffer = find_buffer(buffer_string)
        except:
            print("Buffer not set")


class Report():
    """Creates instances of the PMST report object.
    """

    _FORMAT_DICT = {
        1: "PDF",
        2: "HTML",
        3: "Undefined",
    }

    def __init__(self, file, **kwargs):
        self.date = None
        self.email = None
        self.soup = None
        self.buffer = None
        self.file_type = None
        self.url_list = None
        self.kef_list = None
        self.park_list = None
        self.heritage_list = None
        self.biota_list = None
        self.description = None
        self._set_file_type(file)
        self._make_soup(file)
        self._set_buffer()
        self._get_urls()
        #self.get_kefs() - works, commented to stop hitting site
        self.get_parks()
        self.get_date()

    def _set_file_type(self, file):
        """Checks if the file is a PDF or a HTML
        """
        if file.upper().endswith('.PDF'):
            self.file_type = 1
        elif file.upper().endswith('.HTML'):
            self.file_type = 2
        else:
            raise ValueError('File extension must be html or PDF')

    def _make_soup(self, file):
        """Creates BS4 object from html file
        """
        try:
            with open(file) as html:
                self.soup = BeautifulSoup(html, "lxml")
        except:
            print("Unable to create BS4 object")

    def _set_buffer(self):
        """Set the buffer based on the PMST
        """
        try:
            buffer_string = self.soup.find(
                        "span", text=re.compile(r'(Buffer:)')
                    ).text
        except:
            print("No buffer found")

        def find_buffer(string):
            try:
                result = re.search(r"[-+]?\d*\.\d+|\d+", string)
                return float(result.group())
            except:
                print("No date found")

        try:
            self.buffer = find_buffer(buffer_string)
        except:
            print("Buffer not set")

    def _get_urls(self):

        url_list = []

        for url in self.soup.find_all("a"):
            if url.get("href") is None:
                pass
            elif url.get("href") in url_list:
                pass
            else:
                url_list.append(url.get("href"))
        
        url_list.sort()
        self.url_list = url_list

    def get_kefs(self):
        """Gets any Key Ecological Features that are in the PMST report url
        list, looks up the web page and the creates the KEF objects.
        """
        if self.url_list:
            kef_list = []
            for url in self.url_list:
                if re.search('sprat-public/action/kef', url):
                    kef = Kef(
                        url=url,
                        )
                    kef_list.append(kef)

            self.kef_list = kef_list

    def get_parks(self):
        """Gets parks listed in the PMST report. Not yet implemented, no URLs
        for parks in the PMST report
        """
        pass

    def get_heritage(self):
        """Gets heritage places from the PMST report and created heritage
        objects.
        """
        pass

    def get_date(self):
        """Gets date the PMST report was generated. Date always comes in
        DD/MM/YYYY HH:MM:SS format.
        """
        try:
            date_string = self.soup.find(
                        "span", text=re.compile(r'(Report created:)')
                    ).text
        except:
            print("No report date found")

        def find_date(string):
            try:
                result = re.search(r"\d{1,2}/\d{1,2}/\d{2}", string)
                return result.group()
            except:
                print("No date found")

        try:
            self.date = datetime.datetime.strptime(find_date(date_string), "%d/%m/%y")
        except:
            print("Date not set")

    def get_biota(self):
        """Gets any species listed in SPRAT that are in the PMST report url
        list, looks up the SPRAT page and creates the biota object. The
        string the regex looks for is "sprat/public/publicspecies".
        """

        for url in self.url_list:
            if re.search('sprat/public/publicspecies', url):
                response = requests.get(url)
                response.raise_for_status()
                # sprat_id = int(re.search(r'(\d+)$', url).group())
                biota_soup = BeautifulSoup(response.text, "lxml")
                status_text = biota_soup.find(
                    "th", text="EPBC Act Listing Status"
                ).findNext('td').text.upper()

                biota = Biota(
                    biota_soup.find("title").text,
                    url=url,
                    sprat_id=int(re.search(r'(\d+)$', url).group())
                    )

                # looks for threatened status - add code here
                # loop through the threatened list and look for each element in
                # status_text if found, set object status
                # probably a better way to do this with any()
                # Also need to write test that catches the difference between
                # "Endangered" and "critically endangered". If i just look for
                # endangered as a string then critically endangered may be
                # identified incorrectly
                for status in biota.THREATENED_LIST:
                    status_upper = status.upper()
                    if re.search(status_upper, status_text):
                        biota.threatened = status
                        print("found one")

                if biota.sprat_id in self.biota_dict:
                    print("{0} ({2}) - {1} already in dictionary".format(
                        biota.name,
                        biota.sprat_id,
                        biota.threatened,
                    ))
                else:
                    self.biota_dict[biota.sprat_id] = biota
                    print("Writing {0} ({2}) to biota list with ID {1}".format(
                        biota.name,
                        biota.sprat_id,
                        biota.threatened,
                    ))


class ProtectedMatter():
    """Base class for matters protected under the EPBC Act within the PMST
    report.
    """

    def __init__(self, name, url):
        self.name = name
        self.url = url
        self._get_html()

    def _get_html(self):
        response = requests.get(self.url)
        response.raise_for_status()
        self.html = BeautifulSoup(response.text, "lxml")
        print("HTML added to KEF object")


class Place(ProtectedMatter):
    """Base class for places that are protected under the EPBC Act. Inherits
    from the ProtectedMatter base class.
    """
    pass


class Tec(Place):
    """Class for Threatened Ecological Communities (TECs).
    These will have the string "/sprat/public/publicshowcommunity" in the URL.
    """

    TEC_CAT_LIST = [
    'critically endangered',
    'endangered',
    'vulnerable',
    ]

    def __init__(self, name):
        super().__init__(name)
        super()._get_html
        self.set_cat()
        self.url = kwargs.get('url', None)

    def set_cat(self):
        """Method to get the TEC category from the BS4 object
        """
        # include code to get the category from the BS4 object
        lower_cat = str.lower(cat)
        print("Lower cat is {0}".format(lower_cat))
        
        if lower_cat in TEC_CAT_LIST:
            self.cat = lower_cat
            print("It's in the list! Category is {0}".format(lower_cat))
        else:
            raise CatException("Exception: the category argument isn't in the TEC_CAT_LIST")


class Park(Place):
    """Class for parks and protected areas. Uased as bass class for more
    specific rpotected area classes (e.g. marine parks).
    """
    pass


class Amp(Park):
    """Class for Australian marine parks (AMPs)
    """
    pass


class Kef(Place):
    """Class for Key Ecological Features (KEFs)
    """

    def __init__(self, **kwargs):
        self.name = None
        self.html = None
        self.bioregion = []
        self.url_list = []
        self.url = kwargs.get('url', None)
        self._get_html()
        self._get_name()
        self._get_urls()
        self._get_bioregion()

    def _get_html(self):
        response = requests.get(self.url)
        response.raise_for_status()
        self.html = BeautifulSoup(response.text, "lxml")
        print("HTML added to KEF object")

    def _get_urls(self):
        url_list = []
        for url in self.html.find_all("a"):
            if url.get("href") is None:
                pass
            else:
                url_list.append(url.get("href"))
        self.url_list = url_list

    def _get_name(self):
        self.name = self.html.find("h1", {"class": "header-all"}).text

    def _get_bioregion(self):
        for url in self.url_list:
            if re.search("topics/marine/marine-bioregional-plans?", url):
                self.bioregion.append(url)

    def __str__(self):
        return 'Name: {0}, Bioregion: {1}, URL: {2}'.format(
            self.name,
            self.bioregion,
            self.url,
        )


class Biota(ProtectedMatter):
    """Class to represent living things (i.e. species listed under the EPBC
    Act)
    """

    THREATENED_LIST = [
        "Extinct",
        "Extinct in the Wild",
        "Critically Endangered",
        "Endangered",
        "Vulnerable",
        "Conservation Dependent",
        ]

    def __init__(self, name, **kwargs):
        self.name = name
        self.html = None
        self.bioregion = kwargs.get('status', None)
        self.url = kwargs.get('url', None)
        self.sprat_id = kwargs.get('sprat_id', None)
        self.threatened = kwargs.get('threatened', None)
        self.migratory = kwargs.get('migratory', False)
        self.marine = kwargs.get('marine', False)
        self.cetacean = kwargs.get('cetacean', False)
        self.cons_advice = None
        self.listing_advice = None
        self.recovery_plan = None

        self._set_cetacean_status()

    def _get_html(self):
        response = requests.get(self.url)
        response.raise_for_status()
        self.html = BeautifulSoup(response.text, "lxml")
        print("HTML added to Biota object")

    # Code not finished - checks the BS4 object to see if it contains EPBC Act
    # status of "Cetacean"
    #def _set_cetacean_status(self):
    #    if self.html.find('td').find(string="Cetacean"):
    #        self.cetacean = True

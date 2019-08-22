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

    def __init__(self, **kwargs):
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
        """Sets the coordinate type for the query. Used when querying the PMST
        report page.

        Arguments:
            coord_type {str} -- coordinate type from class variable
            _COORD_TYPE_DICT

        Raises:
            ValueError: Exception generated if coord_type argument is not a
            value within _COORD_TYPE_DICT
        """

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
            buffer_string = self._soup.find(
                        "span", text=re.compile(r'(Buffer:)')
                    ).text
        except ValueError:
            print("No buffer found")

        def find_buffer(string):
            try:
                result = re.search(r"[-+]?\d*\.\d+|\d+", string)
                return result.group()
            except ValueError:
                print("No date found")

        try:
            self.buffer = find_buffer(buffer_string)
        except ValueError:
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
        """Initialise class instance.

        Arguments:
            file {html} -- HTML file containing PMST data
        """
        self.date = None
        self._soup = None
        self.buffer = None
        self._coord_dict = None
        self.file_type = None
        self.url_list = None
        self.kef_list = None
        self.park_list = None
        self.tec_list = None
        self.heritage_list = None
        self.biota_list = None
        self.description = None

        self._set_file_type(file)
        self._make_soup(file)
        self._get_buffer()
        self._get_coords()
        self._get_date()
        self._get_urls()
        # self._get_kefs() - works, commented to stop hitting site
        # self._get_tecs()
        # self._get_biota()
        # self._get_parks()
        self._get_heritage()

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
                self._soup = BeautifulSoup(html, "lxml")
        except ValueError:
            print("Unable to create BS4 object")

    def _get_buffer(self):
        """Get the buffer from PMST and set the attribute on the class
        instance
        """
        try:
            buffer_string = self._soup.find(
                        "span", text=re.compile(r'(Buffer:)')
                    ).text
        except ValueError:
            print("No buffer found")

        def find_buffer(string):
            try:
                result = re.search(r"[-+]?\d*\.\d+|\d+", string)
                return float(result.group())
            except ValueError:
                print("No date found")

        try:
            self.buffer = find_buffer(buffer_string)
        except ValueError:
            print("Buffer not set")

    def _get_coords(self):
        """Get coordinates from PMST and set the attribute on the class
        instance
        """
        coord_string = self._soup.find(
                        "span", text=re.compile(r"[-+]?\d*\.\d+ [-+]?\d*\.\d+")
                    ).text

        coord_dict = {}

        try:
            coord_list = re.findall(r'[-+]?\d+.\d+', coord_string)
            print(coord_list)

            # empy list to append coordinates and make x,y pairs
            coord_pair = []
            # counter to serve as key in dict
            key = 1

            for coord in coord_list:
                # adds a coordinate if the coord_pair list isn't full (i.e.
                # length = 2)
                if len(coord_pair) < 2:
                    coord_pair.append(float(coord))
                # If coord_pair list is a pair, add as value to the dict
                # with key counter as key, empty the coord_pair list and
                # increment the key counter. Finally add the coordinate to the
                # empty list
                elif len(coord_pair) == 2:
                    coord_dict[key] = coord_pair
                    coord_pair = []
                    key += 1
                    coord_pair.append(coord)
                # add the final coor_pair list, as the loop doesn't catch this
                # one
                coord_dict[key] = coord_pair
        except ValueError:
            print("Nope")

        self._coord_dict = coord_dict

    def _get_date(self):
        """Gets date the PMST report was generated. Date always comes in
        DD/MM/YYYY HH:MM:SS format.
        """
        try:
            date_string = self._soup.find(
                        "span", text=re.compile(r'(Report created:)')
                    ).text
        except ValueError:
            print("No report date found")

        def find_date(string):
            try:
                result = re.search(r"\d{1,2}/\d{1,2}/\d{2}", string)
                return result.group()
            except ValueError:
                print("No date found")

        try:
            self.date = datetime.datetime.strptime(
                find_date(date_string),
                "%d/%m/%y",
                )
        except ValueError:
            print("Date not set")

    def _get_urls(self):
        """Gets URLs from BS4 object. Requires PMST report to have been
        created for the Report object.
        """
        url_list = []

        if not self._soup:
            print("_soup attribute for Report object does not exist.")
            return None

        try:
            for url in self._soup.find_all("a"):
                if url.get("href") is None:
                    pass
                elif url.get("href") in url_list:
                    pass
                else:
                    url_list.append(url.get("href"))
            url_list.sort()
            self.url_list = url_list
        except ValueError:
            print("Unable to get URLs from PMST report.")

    def _get_kefs(self):
        """Gets any Key Ecological Features that are in the PMST report url
        list, looks up the web page and the creates the KEF objects.
        """

        kef_re_string = 'sprat-public/action/kef'
        kef_list = []

        if self.url_list:
            kef_url_list = [
                url for url in self.url_list if re.search(
                    kef_re_string, url
                    )]
            for url in kef_url_list:
                kef = Kef(url=url)
                kef_list.append(kef)
        else:
            pass

        self.kef_list = kef_list

    def _get_parks(self):
        """Gets parks listed in the PMST report. Not yet implemented, no URLs
        for parks in the PMST report. Might be better to get these through a
        spatial query - CAPAD 2016 is the data source that the PMST reports
        point to
        """
        pass

    def _get_tecs(self):
        """Gets TECs.
        """

        tec_re_string = 'cgi-bin/sprat/public/publicshowcommunity'
        tec_list = []

        if self.url_list:
            try:
                tec_url_list = [
                    url for url in self.url_list if re.search(
                        tec_re_string, url
                        )]
                for url in tec_url_list:
                    tec = Tec(
                        url=url,
                        )
                    tec_list.append(tec)
            except ValueError:
                print("Unable to create TEC from URL list")
        else:
            print("URL list for report object does not exist. "
                  "Unable to get TECs")

        self.tec_list = tec_list

    def _get_heritage(self):
        """Gets heritage places from the PMST report and created heritage
        objects.
        """

        heritage_re_string = "www.environment.gov.au/cgi-bin/ahdb/"
        heritage_list = []

        try:
            heritage_url_list = [
                url for url in self.url_list if re.search(
                    heritage_re_string, url
                    )]
            for url in heritage_url_list:
                heritage = Heritage(
                    url=url,
                    )
                heritage_list.append(heritage)
        except ValueError:
            print("Attribute url_list does not contain valid urls")

        self.heritage_list = heritage_list

    def _get_biota(self):
        """Gets any species listed in SPRAT that are in the PMST report url
        list, looks up the SPRAT page and creates the biota object. The
        string the regex looks for is "sprat/public/publicspecies".
        """

        if self.url_list:
            biota_list = []
            for url in self.url_list:
                if re.search('/cgi-bin/sprat/public/publicspecies', url):
                    biota = Biota(
                        url=url,
                    )
                    biota_list.append(biota)

            self.biota_list = biota_list


class ProtectedMatter():
    """Base class for matters protected under the EPBC Act within the PMST
    report.
    """

    def __init__(self, **kwargs):
        """Dunder method to initialise the class. Can accept **kwargs.
        Recommend passing url as kwarg if available, as url is used to
        fetch the html that gets scraped.

        Arguments:
            name {str} -- Keyword argument, name of the Protected Matter
            url {str} -- Keyword argument, URL for the Protected Matter

        """
        self.name = None
        self.url = kwargs.get('url', None)
        self._soup = None
        self._get_html()

    def _get_html(self):
        response = requests.get(self.url)
        response.raise_for_status()
        self._soup = BeautifulSoup(response.text, "lxml")
        print(f"Protected Matter added to object from url {self.url}")

    def __str__(self):
        return "ProtectedMatter object\n  Name: {0}\n  URL: {1}".format(
            self.name, self.url
            )


class Place(ProtectedMatter):
    """Base class for places that are protected under the EPBC Act. Inherits
    from the ProtectedMatter base class.
    """
    pass


class Heritage(Place):
    """Base class for heritage places (World, Commonwealth or National
    heritage).

    Arguments:
        Place {class} -- Heritage inherits from class Place
    """

    HERITAGE_TYPE_DICT = {
        1: "World heritage place",
        2: "National heritage place",
        3: "Commonwealth heritage place",
    }

    def __init__(self, url):
        self.name = None
        self.category = None  # category of heritage place
        self.type = None  # type of heritage place (e.g. national, world etc.)
        self.status = None  # status (listed, application etc.)
        self.id = None  # ID form the AHDB - 6 digit int - PK from DB?
        self.url = url
        self._soup = None
        self._get_html()


class Tec(Place):
    """Class for Threatened Ecological Communities (TECs).
    These will have the string "/sprat/public/publicshowcommunity" in the URL.
    """

    # The order of this list is important, need to look for critically
    # endangered first, else 'endangered' may give an incorrect match
    TEC_CAT_LIST = [
        'Critically Endangered',
        'Endangered',
        'Vulnerable',
    ]

    def __init__(self, url):
        super().__init__(url)
        self.url = url
        self.category = None
        self.get_name()
        self.set_cat()

    def get_name(self):
        self.name = self._soup.find(
            "title",
        ).text

    def set_cat(self):
        for category in self.TEC_CAT_LIST:
            regex = re.compile(category)
            print(r"Searching for {0}".format(category))
            if self._soup.find("td", text=regex):
                self.category = category
                print(r"Category set to {0}".format(self.category))
                break
            else:
                print("No match for category found")


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
        "Extinct in the Wild",
        "Extinct",
        "Critically Endangered",
        "Endangered",
        "Vulnerable",
        "Conservation Dependent",
        ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sprat_id = None
        self.threatened = None
        self.migratory = None
        self.marine = None
        self.cetacean = None
        self.cons_advice = None
        self.listing_advice = None
        self.recovery_plan = None
        self.get_name()
        self.set_cat()

    def get_name(self):
        self.name = self._soup.find(
            "title",
        ).text

    def set_cat(self):
        for category in self.THREATENED_LIST:
            regex = re.compile(category)
            print(r"Searching for {0}".format(category))
            if self._soup.find("strong", text=regex):
                self.category = category
                print(r"Threatened set to {0}".format(self.category))
                break
            else:
                print("No match for category found")

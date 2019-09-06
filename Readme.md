
# PMST Project

This project is intended to automate the process of extracting and summarizing data from a Protected Matters Search Tool (PMST) Report. It is written entirely in Python 3.7; no support for other versions of Python is provided.

This is the first time I've generated documentation for a project. It's more detailed than it probably needs to be, as much of the information here is self-evident in the Python code. However, better to have too much information than not enough.

## Dependencies

There are several dependancies for this project from the Python 3.7 standard library and PyPI:

* PyPI packages:
  * [Beautiful Soup (4.4.0)](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#) - scraping HTML
  * [Requests (2.22.0)](https://2.python-requests.org/en/master/) - http requests
* Standard library packages:
  * [re (Python 3.7)](https://docs.python.org/3/library/re.html) - regular expressions for selecting elements of the BS4 objects used to represent the PMST report
  * [datetime (Python 3.7)](https://docs.python.org/3/library/datetime.html) - date type

THe PMST project has only been tested using the versions listed above.

## Classes

All of the classes in `pmst.py` are described below (including attributes and methods). While types have been provided in the descriptions of class attributes and method arguments, they are not currently statically typed in the classes in `pmst.py`. The types are intended to aid indatabase schema development, and who knows...maybe I'll implement type hints or static typing.

The inheritance relationships between classes are shown in the figure below (generated using PlantUML at <http://plantuml.com/).> The file containing the PlantUML code is here.

![pmst_class_diagram](/static/pmst_class_diagram.png)

### class Report()

Creates report objects based on the html file that is passed to it. The report object is required to generate the protected matters objects and scrape the Department of the Environment and Energy website - all of the functionality of the app requires a report object to work.

#### Report() Attributes

* FORMAT_DICT (dictionary) - dictionary containing report types (PDF, html or undefined), intended to be used as a private attribute within the class
* date (datetime) - the date the PMST report was generated as Python datetime.datetime object
* email (string) - the email address the PMST report was sent to
* soup (bs4 object) - BS4 object based on the HTML file passed to \_\_init__
* file_type (string) - file type (PDF, html or undefined), created by \_get_file_type() method
* url_list (list) - list containing URLs (as strings) within the report, created by get_urls() method
* kef_list (list) - list containing KEFs (as instances of the Kef class) within the PMST report, created by the get_kefs() method
* park_list (list) - list containing parks (as instances of the Park class) within the PMST report, created by the get_parks() method. Not currently implemented
* heritage_list (list) - list containing heritage places (as instances of the Heritage class) within the PMST Report, created by the get_heritage() method
* biota_list (list) - list containing biota (as instances of the Biota class) within the PMST report, created by the get_biota() method
* description (string) - a description of the report

#### Report() Methods

* \_\_init__(self, file, **kwargs) - overrides the default initialisation method.
  * file must be a html file containing the PMST report generated by the PMST Search Tool web application
  * kwargs can be passed for any of the other attributes
* \_set_file_type(self, file) - sets the file_type attribute based on the extention of the file passed to the Report object when created
* \_make_soup(self, file) - creates BS4 object and sets it as the soup attribute
* get_urls(self) - uses a regex to look for all the URLs in the pmst report and stores then in the url_list attribute as a string
* get_kefs(self) - uses a regex to search through the url_list attribute for KEF URLs, request each URL, creates the associated instance of the Kef class and adds it to the kef_list
* get_parks(self) - uses a regex to search through the url_list attribute for park URLs, request each URL, creates the associated instance of the Park class and adds it to the park_list
* get_heritage(self) - TO DO
* get_biota(self) - TO DO
* get_date(self) - TO DO
* get_email(self) - gets the email address from the PMST report

### class Query()

#### Query() Attributes

#### Query() Methods

### class ProtectedMatter()

Base class for all other Protected Matters

#### ProtectedMatters() Attributes

* name - string

#### ProtectedMatters() Methods

* \_\_init__

### class Place(ProtectedMatter)

Base class for all Protected Matters that are places (i.e. clearly defined named spatial extent). It inherits from the ProtectedMatter base class.

#### Place() Attributes

* Name - inherits from ProtectedMatter
* Place - dictionary of x,y coordinates in WGS84
* Jurisdiction - string of the jurisdiction, selected from class variable JURIS_DICT
* JURIS_DICT - dictionary containig jurisdictions

#### Place() Methods

* \_\_init__
* super() from ProtectedMatter - gets the name expression from the parent class

### class Tec(Place, biota)

Class for threatened ecological communities (TECs). Inherits from Place.

#### Tec() Attributes

* status - string - status under the EPBC Act, same list as threatened fauna. Inherit this from fauna class

#### Tec() Methods

* \_\_init__()

# PlantUML Code for Class Diagrams

Use this with PlantUML to generate class digrams.

## Report Class

```PlantUML
@startuml
' Base class for all protected matters
class Report{
-_FORMAT_DICT : dictionary
+description : string
+date : datetime.datetime
+_soup : BeautifulSoup object
+buffer : float
+coord_dict : dictionary
+file_type : string
+url_list : list
+kef_list : list
+park_list : list
+heritage_list : list
+biota_list : list
+description : string

-__init__(self, file, **kwargs)
+_set_file_type(self, file)
+_make_soup(self, file)
+_get_buffer(self)
+_get_coords(self)
+_get_date(self)
+_get_urls(self)
+get_kefs(self)
+get_parks(self)
+get_heritage(self)
+get_biota(self)
}
@enduml
```

## ProtectedMatters Class Tree

Shows the super and subclasses used to create Protected Matters objects.

```PlantUML
@startuml
ProtectedMatter <|-- Place
Place <|-- Heritage

' Base class for all protected matters
class ProtectedMatter{
+name: string
+url: string
+_soup: BeautifulSoup object

-__init__(self, **kwargs)
-_get_html(self)
+__str__(self)
}

class Place{
+^name: string
+^url: string
+^_soup: BeautifulSoup object

-^__init__(self, **kwargs)
-^_get_html(self)
+^__str__(self)
}

class Heritage{
+^name: string
+^url: string
+^_soup: BeautifulSoup object
+HERIAGE_TYPE_DICT = dictionary
+category: string

-^__init__(self, **kwargs)
-^_get_html(self)
+^__str__(self)
}
@enduml
```

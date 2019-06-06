# Filename: fix_it.py
# Python 3.7
# Notes:
#    This is a module of main_process.py
#    Not to be run independently -- Use 'python main_process.py'
#    To view a demo of the fix_it routine -- Run 'python fix_it_demo.py'
# Purpose: Correct problematic data

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
from email.utils import parseaddr
from urllib.parse import urlparse
import pprint
import operator

import element_to_dictionary

pp = pprint.PrettyPrinter(indent=4, width=20)

#================================#
#     Construct dictionaries     #
#================================#

streets_issue = defaultdict(int)
us_states_issue = defaultdict(int)
us_states_problem = defaultdict(int)
cities_issue = defaultdict(int)
cities_problem = defaultdict(int)
phones_issue = defaultdict(int)
emails_issue = defaultdict(int)
websites_issue = defaultdict(int)
zipcodes_issue = defaultdict(int)
tiger_issue = defaultdict(int)

streets_fix = defaultdict(int)
streets_dict = defaultdict(dict)
cities_fix = defaultdict(int)
cities_dict = defaultdict(dict)
us_states_fix = defaultdict(int)
us_states_dict = defaultdict(dict)

zipcodes_fix = defaultdict(int)
zipcodes_dict = defaultdict(dict)
phones_fix = defaultdict(int)
phones_dict = defaultdict(dict)
tiger_fix = defaultdict(int)
tiger_dict = defaultdict(dict)

house_fix = defaultdict(int)
house_dict = defaultdict(dict)
cuisine_fix = defaultdict(int)
cuisine_dict = defaultdict(dict)

counts = defaultdict(int)
value_issue = defaultdict(list)

bad_keys = defaultdict(int)
way_id_bad = defaultdict(int)
node_id_bad = defaultdict(int)
way_node_reference_bad = defaultdict(int)

#===========================================#
#     Initialize lists and dictionaries     #
#===========================================#

ok_streets = [ 'Americas', 'Avenue', 'Boulevard', 'Broadway', 'Circle', 'Court', 'Drive', 'East', 'Lane',
               'North', 'Parkway', 'Place', 'Plaza', 'Road', 'South', 'Square', 'Street', 'Terrace', 'Walk',
               'Way', 'West']
other_city = ['Union City', 'West New York', 'North Bergen', 'Weehawken', 'Long Island City', 'Roosevelt Island',
              'Queens', 'Guttenberg', 'Astoria', 'Hoboken', 'Jersey City', 'Morristown']
ok_domains = ['.com', '.org', '.net', '.edu', '.gov', '.us', '.nyc', '.biz', '.info', '.io', '.it',
              '.co', '.site', '.cz', '.hu', '.int']
uws_zips = ['10023', '10024', '10025']
abbreviations = ['st', 'nd', 'rd', 'th']
phone_prefixes = ['212 ', '(212', '646 ', '(646', '212-', '646-', '917 ', '(917', '917-', '800 ', '800-', 
                  '(800', '718-', '(888', '845-', '855-']

direction_mapping = { "N.": "North",
                      "E.": "East",
                      "S.": "South",
                      "W.": "West",
                      "N ": "North ",
                      "E ": "East ",
                      "S ": "South ",
                      "W ": "West "}

street_mapping = { "St": "Street",    # Street mapping is specific to this dataset
                  "St.": "Street",
               "street": "Street",
                   "st": "Street",
                  "st.": "Street",
                   "pl": "Place",
                  "pl.": "Place",
                "place": "Place",
                   "Pl": "Place",
                  "Pl.": "Place",
               "avenue": "Avenue",
                  "ave": "Avenue",
                 "ave.": "Avenue",
                  "Ave": "Avenue",
                 "Ave.": "Avenue",
                "Avene": "Avenue",
               "Aveneu": "Avenue",
          "Avenue,#392": "Avenue",
                   "dr": "Drive",
                  "dr.": "Drive",
                   "Dr": "Drive",
                  "Dr.": "Drive",
                    "N": "North",
                    "S": "South",
                    "E": "East",
                    "W": "West"}    # e.g. Central Park West

typo_mapping = {"nwe": "new",
               "yoro": "york",
               "ykrk": "york",
               "ykro": "york"}

#====================================#
#     Define regular expressions     #
#====================================#

phone_re = re.compile(r"^(\+1\s?-?\(?\)?)(\d{3})\D*(\d{3})\D*(\d{4})$")  # r: RE must process backslash as escape
email_re = re.compile(r"[\w.-]+@[\w.-]+")
website_re = re.compile(r"^(http\:\/\/)?(https\:\/\/)?([\w.-])*[\w-]+\.([a-zA-Z][a-zA-Z][a-zA-Z]?[a-zA-Z]?)(\/[\w/.#?=%&,!+()-]*)?$")
basic_re = re.compile(r"^[a-zA-Z0-9'_.,;:=–’>!´é~êçóíáô®@½·\"\-\(\)\&\/\+\s]+$")   # Note: Characters are specific to this dataset

# ================================================== #
#                Helper Function                     #
# ================================================== #

#  Clears the global dictionaries
def initialize():
    """Clears the dictionaries and returns a boolean."""
    try:
        counts.clear()

        streets_issue.clear()
        us_states_issue.clear()
        us_states_problem.clear()
        cities_issue.clear()
        cities_problem.clear()
        phones_issue.clear()
        emails_issue.clear()
        websites_issue.clear()
        zipcodes_issue.clear()
        tiger_issue.clear()
        value_issue.clear()
        
        streets_fix.clear()
        streets_dict.clear()
        cities_fix.clear()
        cities_dict.clear()
        us_states_fix.clear()
        us_states_dict.clear()
        
        zipcodes_fix.clear()
        zipcodes_dict.clear()
        phones_fix.clear()
        phones_dict.clear()
        tiger_fix.clear()
        tiger_dict.clear()
        
        house_fix.clear()
        house_dict.clear()
        cuisine_fix.clear()
        cuisine_dict.clear()
        
        bad_keys.clear()
        way_id_bad.clear()
        node_id_bad.clear()
        way_node_reference_bad.clear()
    except:
        return None
    
    return True

# =================================================================== #
#               Functions to correct the values                       #
#                 and related helper functions                        #
# =================================================================== #

def update_street_city(street_city, mapping):
    """Lookup function returns the mapping or None.
    
    Arguments:
    street_city -- the item to be mapped
    mapping -- the mapping lookup dictionary to use
    """
    try:
        street_city =  mapping[street_city]
    except:
        print ('Street or City mapping exception!')
        return None
    
    return street_city

def street_problem(name, street, node_or_way):
    """Function fix_streets helper eliminates street and returns None.
    
    Arguments:
    name -- name of street passed from function fix_streets
    street -- street kind passed from function fix_streets
    node_or_way -- node_or_way element tag passed from function fix_streets
    """
    print (node_or_way, ': Street problem removed from dataset -- name: ', name, '  street: ', street)
    streets_issue[street] += 1
    counts['value eliminated'] += 1
    return None                         # Eliminate problematic data from dataset

def fix_streets(name, node_or_way):
    """Correct street dirty data if possible and return corrected value or None if data is eliminated.
    
    Arguments:
    name -- the value of the addr:street key
    node_or_way -- Indicates XML element tag is a <node> or <way>
    """
    if not name or name.isspace():        # Check for null characters: None, False, '', 0, and ' '
        print (node_or_way, ': Street problem removed from dataset -- street is null or whitespace  ', name)
        streets_issue[name] += 1
        counts['value eliminated'] += 1
        return None                         # Eliminate problematic data from dataset
    
    name = name.strip()
    flag = True
    
    try:
        name = name.rsplit(' ', 1)     # name[0] + name[1] where name[1] is the street
    except:
        flag = False
    
    if len(name) == 1:                # name is a single word e.g. Broadway
        street = name[0]
        name = name[0]
        flag = False
    else:
        street = name[1]
        name = name[0]
    
    if street in street_mapping.keys():
        # Standardize street abbreviations
        better_street = update_street_city(street, street_mapping)
        if better_street:
            streets_fix[street] += 1
            streets_dict[street][better_street] = streets_fix[street]
            # print ('Street fixed:  ', street, "=>", better_street)
            street = better_street
        else:
            return street_problem(name, street, node_or_way)
            
    for k in direction_mapping.keys():
        if k in name:
            # Remove periods e.g. W. 86th => West 86th
            # Convert abbreviations e.g. W 79th => West 79th
            better_name = name.replace(k, update_street_city(k, direction_mapping))
            streets_fix[name] += 1
            streets_dict[name][better_name] = streets_fix[name]
            # print ('Street name fixed:  ', name, "=>  name: ", better_name, "  street: ", street)
            name = better_name
    
    if street.isalnum():                          # Alphanumeric characters only
        if street not in ok_streets:
            if street[-2:] in abbreviations:      # Examine the last 2 characters e.g. 86th
                print ('Street with issue allowed ... name: ', name, '  street: ', street)  
            else:
                return street_problem(name, street, node_or_way)
    else:
        return street_problem(name, street, node_or_way)
    
    if flag:
        name = name + ' ' + street
    
    return name

def fix_city(name, node_or_way):
    """Correct city dirty data if possible and return corrected value or None if data is eliminated.
    
    Arguments:
    name -- the value of the addr:city key
    node_or_way -- Indicates XML element tag is a <node> or <way>
    """
    if not name or name.isspace():
        print (node_or_way, ': City is null -- removed from dataset  ', name)
        cities_problem[name] += 1
        counts['value eliminated'] += 1
        return None                     # Eliminate problematic data from dataset
    
    name = name.strip()
    
    # Only alphabetical letters, spaces or ","
    if not all(char.isalpha() or char.isspace() or ',' or '.' for char in name):
        print (node_or_way, ': City contains problem characters -- removed from dataset  ', name)
        cities_problem[name] += 1
        counts['value eliminated'] += 1
        return None                     # Eliminate problematic data from dataset
    
    namelow = name.lower()
    
    for k in typo_mapping.keys():   # Fix spelling
        if k in namelow:
            namelow = namelow.replace(k, update_street_city(k, typo_mapping))
            better_name = namelow.title()
            cities_fix[name] += 1
            cities_dict[name][better_name] = cities_fix[name]
            # print ('City spelling fixed:  ', name, "=>", better_name)
            name = better_name
    
    ok_city = ['New York', 'New York City']
    ok_city_lower = ['new york', 'new york city']

    if namelow in ok_city_lower and name not in ok_city:  # Fix titlecase
        better_name = name.title()
        cities_fix[name] += 1
        cities_dict[name][better_name] = cities_fix[name]
        # print ('City title case fixed:  ', name, "=>", better_name)
        name = better_name

# Fix abbreviations or state e.g. 'New York NY' or 'New York, NY'
    if any(word in namelow for word in ['ny', 'nyc', 'nyy']):
        better_name = 'New York'
        cities_fix[name] += 1
        cities_dict[name][better_name] = cities_fix[name]
        # print ('City abbreviation fixed:  ', name, "=>", better_name)
        name = better_name
    
    if namelow == 'west new york' and name != 'West New York':   # Fix titlecase
        better_name = name.title()
        cities_fix[name] += 1
        cities_dict[name][better_name] = cities_fix[name]
        # print ('City West New York title case fixed:  ', name, "=>", better_name)
        name = better_name
    # Change New York City to New York and fix punctuation e.g. 'New York,' in city name
    elif name != 'West New York' and 'new york' in namelow and len(name) > 8:
        better_name = name[:8]
        cities_fix[name] += 1
        cities_dict[name][better_name] = cities_fix[name]
        # print ('City extra end characters fixed:  ', name, "=>", better_name)
        name = better_name
    
    if name not in ok_city:          # Identified a problem
        cities_issue[name] += 1      # Record the problem
        if name not in other_city:   # Identified a problem; allow certain cities in NJ
            print (node_or_way, ': Problem city -- removed from dataset  ', name)
            cities_problem[name] += 1
            counts['value eliminated'] += 1
            return None                # Eliminate problematic data from dataset 
    
    return name

def fix_state(name, node_or_way):
    """Correct state dirty data if possible and return corrected value or None if data is eliminated.
    
    Arguments:
    name -- the value of the addr:state key
    node_or_way -- Indicates XML element tag is a <node> or <way>
    """
    if not name or name.isspace():
        print (node_or_way, ': State is null -- removed from dataset  ', name)
        us_states_problem[name] += 1
        counts['value eliminated'] += 1
        return None                      # Eliminate problematic data from dataset
    
    name = name.strip().upper()
    namelow = name.lower()
    
    if '.' in name or ',' in name:
        better_name = name.replace('.', '').replace(',', '')    # Remove periods or commas e.g. 'N.Y.' => 'NY'
        us_states_fix[name] += 1
        us_states_dict[name][better_name] = us_states_fix[name]
        # print ('State punctuation fixed:  ', name, "=>", better_name)
        name = better_name
    
    if namelow in ['new york', 'new york city']:   # Fix state to NY
        better_name = 'NY'
        us_states_fix[name] += 1
        us_states_dict[name][better_name] = us_states_fix[name]
        # print ('State fixed:  ', name, "=>", better_name)
        name = better_name
    
    if namelow == 'ny' and name != 'NY':   # Fix to uppercase
        better_name = 'NY'
        us_states_fix[name] += 1
        us_states_dict[name][better_name] = us_states_fix[name]
        # print ('State case fixed:  ', name, "=>", better_name)
        name = better_name
               
    if 'ny' in namelow and len(name) > 2:   # Fixes NYC, NYY, 'NY NY' and similar NY issues
        better_name = 'NY'
        us_states_fix[name] += 1
        us_states_dict[name][better_name] = us_states_fix[name]
        # print ('State fixed:  ', name, "=>", better_name)
        name = better_name
    
    if not name.isalpha():       # string contains only alphabetical characters and no spaces
        print (node_or_way, ': State contains problem characters -- removed from dataset  ', name)
        us_states_problem[name] += 1
        counts['value eliminated'] += 1
        return None
    
    if name != 'NY':                 # Identified a problem
        us_states_issue[name] += 1   # Record the problem
        if name != 'NJ':             # Identified a problem; allow 'NJ' state data
            print (node_or_way, ': Problem state removed from dataset  ', name)
            us_states_problem[name] += 1
            counts['value eliminated'] += 1
            return None                # Eliminate problematic data from dataset 
    
    return name

def zip_test(zip, node_or_way):
    """Function fix_zipcodes helper checks zip code and returns it if valid or returns None to eliminate.
    
    Arguments:
    zip -- the zip code to be examined, passed from function fix_zipcodes
    node_or_way -- node_or_way element tag passed from function fix_zipcodes
    """
    if not zip or zip.isspace():
        print (node_or_way, ': Zipcode is null -- removed from dataset  ', zip)
        zipcodes_issue[zip] += 1
        counts['value eliminated'] += 1
        return None
    
    if zip.isdigit() and len(zip) == 5:        # zipcode contains only 5 digits
        return zip
    else:
        print (node_or_way, ': Zipcode is not valid -- removed from dataset  ', zip)
        zipcodes_issue[zip] += 1
        counts['value eliminated'] += 1
        return None

def fix_zipcodes(name, node_or_way):
    """Correct zip code dirty data if possible and return corrected value or None if data is eliminated.
    
    Arguments:
    name -- the value of the addr:postcode key
    node_or_way -- Indicates XML element tag is a <node> or <way>
    """
    name = name.strip()
    
    if '-' in name and len(name) == 10:   # Zip+4 strip off the plus 4
        better_name = name[:5]
        zipcodes_fix[name] += 1
        zipcodes_dict[name][better_name] = zipcodes_fix[name]
        # print ('Zip+4 fixed:  ', name, "=>", better_name)
        name = better_name
    
    if 'NY' in name:               # Strip out NY
        better_name = name[-5:]    # From end of string
        zipcodes_fix[name] += 1
        zipcodes_dict[name][better_name] = zipcodes_fix[name]
        # print ('Zip code fixed:  ', name, "=>", better_name)
        name = better_name
    
    return zip_test(name, node_or_way)
    
def fix_phone(name, node_or_way):
    """Correct phone number dirty data if possible and return corrected value or None if data is eliminated.
    
    Arguments:
    name -- the value of the phone key
    node_or_way -- Indicates XML element tag is a <node> or <way>
    """
    if not name or name.isspace():
        print (node_or_way, ': Phone is null -- removed from dataset  ', name)
        phones_issue[name] += 1
        counts['value eliminated'] += 1
        return None
    
    name = name.strip()
    
    if name[0] == '+' and name[1] != '1':
        better_name = name.replace('+', '+1 ')      # Fix '+' without '1'
        phones_fix[name] += 1
        phones_dict[name][better_name] = phones_fix[name]
        # print ('Phone fixed:  ', name, "=>", better_name)
        name = better_name
    
    if '.' in name:
        better_name = name.replace('.', '-')     # Replace any periods in phone number with a dash
        phones_fix[name] += 1
        phones_dict[name][better_name] = phones_fix[name]
        # print ('Phone fixed:  ', name, "=>", better_name)
        name = better_name
    
    if '001' in name[:3]:                        # Begining of string
        better_name = name.replace('001', '+1')
        phones_fix[name] += 1
        phones_dict[name][better_name] = phones_fix[name]
        # print ('Phone fixed:  ', name, "=>", better_name)
        name = better_name
        
    if '1 ' in name[:2] or '1-' in name[:2]:
        better_name = '+1 ' + name[2:]
        phones_fix[name] += 1
        phones_dict[name][better_name] = phones_fix[name]
        # print ('Phone fixed:  ', name, "=>", better_name)
        name = better_name
        
    if any(prefix in name[:4] for prefix in phone_prefixes):
        better_name = '+1 ' + name
        phones_fix[name] += 1
        phones_dict[name][better_name] = phones_fix[name]
        # print ('Phone fixed:  ', name, "=>", better_name)
        name = better_name
        
    if ('212' in name[:3] or '646' in name[:3]) and name[3].isdigit():
        better_name = '+1 ' + name
        phones_fix[name] += 1
        phones_dict[name][better_name] = phones_fix[name]
        # print ('Phone fixed:  ', name, "=>", better_name)
        name = better_name
    
    if ' ' in name[-4:]:
        end = len(name) - 5
        better_name = name[:end] + name[-5:].replace(' ', '')
        phones_fix[name] += 1
        phones_dict[name][better_name] = phones_fix[name]
        # print ('Phone fixed:  ', name, "=>", better_name)
        name = better_name
    
    match = phone_re.search(name)
    if not match:
        phones_issue[name] += 1
        print (node_or_way, ': Phone problem -- removed from dataset  ', name)
        counts['value eliminated'] += 1
        return None
    
    return name

def fix_email(name, node_or_way):
    """Checks email address and returns it if valid or returns None if data is eliminated.
    
    Arguments:
    name -- the value of the email key
    node_or_way -- Indicates XML element tag is a <node> or <way>
    """
    if not name or name.isspace():
        print (node_or_way, ': Email is null -- removed from dataset  ', name)
        emails_issue[name] += 1
        counts['value eliminated'] += 1
        return None
    
    name = name.strip().lower()
    
    first_parse = parseaddr(name)
    second_parse = not email_re.search(name)    # search() returns None (False) if no match can be found
                                                # If match found, a match object instance is returned
    third_parse = not first_parse[1].endswith(tuple(ok_domains))
    
    if first_parse == ('', '') or second_parse or third_parse:
        emails_issue[name] += 1
        print (node_or_way, ': Email problem -- removed from dataset  ', name)
        counts['value eliminated'] += 1
        return None
    
    return name

def fix_website(name, node_or_way):
    """Checks website URL and returns it if valid or returns None if data is eliminated.
    
    Arguments:
    name -- the value of the website or url key
    node_or_way -- Indicates XML element tag is a <node> or <way>
    """
    if not name or name.isspace():
        print (node_or_way, ': Website is null -- removed from dataset  ', name)
        websites_issue[name] += 1
        counts['value eliminated'] += 1
        return None
    
    name = name.strip().lower()
    
    flag_1 = True
    first_parse = urlparse(name)
    
    if (first_parse.scheme == '') and (first_parse.netloc == '') and (first_parse.path == ''):
        flag_1 = False
    
    match = website_re.search(name)
    
    flag_2 = False
    for domain in ok_domains:
        if domain in name:
            flag_2 = True
            break
        else:
            flag_2 = False
    
    if not (match and flag_1 and flag_2):
        websites_issue[name] += 1
        print (node_or_way, ': Website problem -- removed from dataset  ', name)
        counts['value eliminated'] += 1
        return None
    
    return name

def fix_tiger_no(name, node_or_way):
    """Correct TIGER dirty data if possible and return corrected value or None if data is eliminated.
    
    Arguments:
    name -- the value of the tiger:reviewed key
    node_or_way -- Indicates XML element tag is a <node> or <way>
    """
    if not name or name.isspace():
        print (node_or_way, ': Tiger reviewed is null -- removed from dataset  ', name)
        tiger_issue[name] += 1
        counts['value eliminated'] += 1
        return None
    
    name = name.strip()
               
    if name in ['; no; no', 'not']:
        better_name = 'no'
        tiger_fix[name] += 1
        tiger_dict[name][better_name] = tiger_fix[name]
        # print ('Tiger fixed:  ', name, "=>", better_name)
        return better_name
    
    stripes = ['yes', 'no', 'aerial']
    
    if name not in stripes:
        tiger_issue[name] += 1
        print (node_or_way, ': TIGER reviewed problem -- removed from dataset  ', name)
        counts['value eliminated'] += 1
        return None
    
    return name

def basic_fix(key, value, node_or_way):
    """Correct value dirty data if possible and return corrected value or None if data is eliminated.
    
    Arguments:
    key -- the child element tag key
    value -- the child element tag value
    node_or_way -- Indicates XML element tag is a <node> or <way>
    """
    if not value or value.isspace():             # None, False, '', 0, and ' '
        print (node_or_way, ':  ', key, ' problem removed from dataset -- value is null or whitespace  ', value)
        value_issue[key].append(value)
        counts['value eliminated'] += 1
        return None
    
    value = value.strip()
    
    if key == "addr:housenumber" and '#' in value:
        better_value = value.replace('#', '')
        # print (key, '  value ', value, '  changed to ', better_value)
        house_fix[value] += 1
        house_dict[value][better_value] = house_fix[value]
        value = better_value
            
    if key == "cuisine":
        if (not value.istitle()) or ('_' in value):
            better_value = value.title().replace('_', ' ')    # consistent case for values, change '_'
            # print (key, '  value ', value, '  changed to ', better_value)
            cuisine_fix[value] += 1
            cuisine_dict[value][better_value] = cuisine_fix[value]
            value = better_value
    
    match = basic_re.findall(value)
    
    if not match:
        print (node_or_way, ':  ', key, ' problem removed from dataset -- value is not allowed  ', value)
        value_issue[key].append(value)
        counts['value eliminated'] += 1
        return None
    
    return value

# ======================================================= #
#               Identity Functions                        #
# ======================================================= #

def is_housenumber(elem):
    """Examine the key of the element tag and return a boolean.
    
    Arguments:
    elem -- the current XML element in the Element Tree iteration
    """
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:housenumber")

def is_amenity(elem):
    """Examine the key of the element tag and return a boolean.
    
    Arguments:
    elem -- the current XML element in the Element Tree iteration
    """
    return (elem.tag == "tag") and (elem.attrib['k'] == "amenity")

def is_name(elem):
    """Examine the key of the element tag and return a boolean.
    
    Arguments:
    elem -- the current XML element in the Element Tree iteration
    """
    return (elem.tag == "tag") and (elem.attrib['k'] == "name")

def is_cuisine(elem):
    """Examine the key of the element tag and return a boolean.
    
    Arguments:
    elem -- the current XML element in the Element Tree iteration
    """
    return (elem.tag == "tag") and (elem.attrib['k'] == "cuisine")

def is_shop(elem):
    """Examine the key of the element tag and return a boolean.
    
    Arguments:
    elem -- the current XML element in the Element Tree iteration
    """
    return (elem.tag == "tag") and (elem.attrib['k'] == "shop")

def is_building(elem):
    """Examine the key of the element tag and return a boolean.
    
    Arguments:
    elem -- the current XML element in the Element Tree iteration
    """
    return (elem.tag == "tag") and (elem.attrib['k'] == "building")

def is_street(elem):
    """Examine the key of the element tag and return a boolean.
    
    Arguments:
    elem -- the current XML element in the Element Tree iteration
    """
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:street")

def is_state(elem):
    """Examine the key of the element tag and return a boolean.
    
    Arguments:
    elem -- the current XML element in the Element Tree iteration
    """
    return (elem.tag == "tag") and (elem.attrib["k"] == "addr:state")

def is_city(elem):
    """Examine the key of the element tag and return a boolean.
    
    Arguments:
    elem -- the current XML element in the Element Tree iteration
    """
    return (elem.tag == "tag") and (elem.attrib["k"] == "addr:city")

def is_zipcode(elem):
    """Examine the key of the element tag and return a boolean.
    
    Arguments:
    elem -- the current XML element in the Element Tree iteration
    """
    return (elem.tag == "tag") and (elem.attrib["k"] == "addr:postcode")

def is_phone(elem):
    """Examine the key of the element tag and return a boolean.
    
    Arguments:
    elem -- the current XML element in the Element Tree iteration
    """
    return (elem.tag == "tag") and (elem.attrib["k"] == "phone")

def is_email(elem):
    """Examine the key of the element tag and return a boolean.
    
    Arguments:
    elem -- the current XML element in the Element Tree iteration
    """
    return (elem.tag == "tag") and (elem.attrib["k"] == "email")

def is_website(elem):
    """Examine the key of the element tag and return a boolean.
    
    Arguments:
    elem -- the current XML element in the Element Tree iteration
    """
    return (elem.tag == "tag") and ( (elem.attrib["k"] == "website") or (elem.attrib["k"] == "url") )

def is_tiger(elem):
    """Examine the key of the element tag and return a boolean.
    
    Arguments:
    elem -- the current XML element in the Element Tree iteration
    """
    return (elem.tag == "tag") and (elem.attrib["k"] == "tiger:reviewed")

def is_inscription(elem):
    """Examine the key of the element tag and return a boolean.
    
    Arguments:
    elem -- the current XML element in the Element Tree iteration
    """
    return (elem.tag == "tag") and ("inscription" in elem.attrib['k'])


# ================================================== #
#               Main Function                        #
# ================================================== #

def fixer(element, node_or_way):
    """Sends the value data out for parsing and returns the corrected value, or None if eliminated, 
       or skips the element.
    
    Arguments:
    element -- the child element tag value
    node_or_way -- Indicates XML element tag is a <node> or <way>
    """
    if is_housenumber(element):
        return basic_fix(element.attrib['k'], element.attrib['v'], node_or_way)
    
    if is_amenity(element):
        return basic_fix(element.attrib['k'], element.attrib['v'], node_or_way)

    if is_name(element):
        return basic_fix(element.attrib['k'], element.attrib['v'], node_or_way)

    if is_cuisine(element):
        return basic_fix(element.attrib['k'], element.attrib['v'], node_or_way)

    if is_shop(element):
        return basic_fix(element.attrib['k'], element.attrib['v'], node_or_way)

    if is_building(element):
        return basic_fix(element.attrib['k'], element.attrib['v'], node_or_way)

    if is_street(element):
        return fix_streets(element.attrib['v'], node_or_way)

    if is_state(element):
        return fix_state(element.attrib["v"], node_or_way)

    if is_city(element):
        return fix_city(element.attrib["v"], node_or_way)

    if is_zipcode(element):
        return fix_zipcodes(element.attrib["v"], node_or_way)

    if is_phone(element):
        return fix_phone(element.attrib["v"], node_or_way)

    if is_email(element):
        return fix_email(element.attrib["v"], node_or_way)

    if is_website(element):
        return fix_website(element.attrib["v"], node_or_way)

    if is_tiger(element):
        return fix_tiger_no(element.attrib["v"], node_or_way)
    
    if is_inscription(element):
        return basic_fix(element.attrib['k'], element.attrib['v'], node_or_way)
    
    return '$skip'    # Ignore the elements not listed above

# ========================================================================= #
#       Functions to print reports of data corrected or eliminated          #
# ========================================================================= #

def print_dictionary(dic, text):
    """Helper function to print a dictionary formatted and returns None.
    
    Arguments:
    dic -- the dictionary to be formatted
    text -- wording related to the dictionary
    """
    print ('\n' + text + ' fixes:')
    
    total = 0
    for key, val in dic.items():            # Python 3 returns a view, NOT a list
        value_list = list(val.items())
        print ('   ', key, ' => ', value_list[0][0], ' :', value_list[0][1])
        total += value_list[0][1]
    
    if text == 'City':
        text = 'Citie'
    if text == 'Tiger no':
        text = "Tiger no'"
    
    print (text + 's' + ' fixed:', total) 
    return

def print_detailed_fixes(counts):
    """Prints a detailed report of data corrections and eliminations, and returns None.
    
    Arguments:
    counts -- a dictionary of the number of data issues
    """
    streets_issue_sort = sorted(streets_issue.items(), key=operator.itemgetter(1))
    streets_issue_sort.reverse()  # Note: In-place reversal
    
    cities_issue_sort = sorted(cities_issue.items(), key=operator.itemgetter(1))
    cities_issue_sort.reverse()  # Note: In-place reversal
    
    cities_problem_sort = sorted(cities_problem.items(), key=operator.itemgetter(1))
    cities_problem_sort.reverse()  # Note: In-place reversal
    
    us_states_issue_sort = sorted(us_states_issue.items(), key=operator.itemgetter(1))
    us_states_issue_sort.reverse()  # Note: In-place reversal
    
    us_states_problem_sort = sorted(us_states_problem.items(), key=operator.itemgetter(1))
    us_states_problem_sort.reverse()  # Note: In-place reversal
    
    zipcodes_issue_sort = sorted(zipcodes_issue.items(), key=operator.itemgetter(1))
    zipcodes_issue_sort.reverse()  # Note: In-place reversal
    
    phones_issue_sort = sorted(phones_issue.items(), key=operator.itemgetter(1))
    phones_issue_sort.reverse()  # Note: In-place reversal
    
    emails_issue_sort = sorted(emails_issue.items(), key=operator.itemgetter(1))
    emails_issue_sort.reverse()  # Note: In-place reversal
    
    websites_issue_sort = sorted(websites_issue.items(), key=operator.itemgetter(1))
    websites_issue_sort.reverse()  # Note: In-place reversal
    
    bad_keys_sort = sorted(bad_keys.items(), key=operator.itemgetter(1))
    bad_keys_sort.reverse()  # Note: In-place reversal
    
    print("\n---------------------------------------------------------")
    print("CONSOLIDATED DETAILS OF DATA CORRECTIONS AND ELIMINATIONS")
    
    print_dictionary(streets_dict, 'Street')      # Street fixes
    
    sum_val = sum(streets_issue.values())
    print ('\nNumber of street issues: {:,}'.format(sum_val), 'streets removed from dataset')
    print ("Street problems: ")
    print ( *streets_issue_sort, sep = "\n" )
    
    print_dictionary(cities_dict, 'City')         # City fixes
    
    sum_val = sum(cities_issue.values())
    print ('\nNumber of cities not in NYC: {:,}'.format(sum_val))
    print ("Cities outside NYC: ")
    print ( *cities_issue_sort, sep = "\n" )
    
    sum_val = sum(cities_problem.values())
    print ('\nNumber of city problems: {:,}'.format(sum_val), 'cities removed from dataset')
    print ("City problems: ")
    print ( *cities_problem_sort, sep = "\n" )
    
    print_dictionary(us_states_dict, 'State')       # State fixes
    
    sum_val = sum(us_states_issue.values())
    print ('\nNumber of state issues: {:,}'.format(sum_val))
    print ("States outside NY: ")
    print ( *us_states_issue_sort, sep = "\n" )
    
    sum_val = sum(us_states_problem.values())
    print ('\nNumber of state problems: {:,}'.format(sum_val), 'states removed from dataset')
    print ("State problems: ")
    print ( *us_states_problem_sort, sep = "\n" )
    
    print_dictionary(zipcodes_dict, 'Zip code')       # Zip code fixes
    
    sum_val = sum(zipcodes_issue.values())
    print ('\nNumber of zipcode issues: {:,}'.format(sum_val), 'zipcodes removed from dataset')
    print ("Zipcode problems: ")
    print ( *zipcodes_issue_sort, sep = "\n" )
    
    print_dictionary(phones_dict, 'Phone')       # Phone fixes
    
    sum_val = sum(phones_issue.values())
    print ('\nNumber of phone number issues: {:,}'.format(sum_val), 'phone numbers removed from dataset')
    print ("Phone problems: ")
    print ( *phones_issue_sort, sep = "\n" )
    
    sum_val = sum(emails_issue.values())
    print ('\nNumber of email address issues: {:,}'.format(sum_val), 'emails removed from dataset')
    print ("email problems: ")
    print ( *emails_issue_sort, sep = "\n" )
    
    sum_val = sum(websites_issue.values())
    print ('\nNumber of website URL issues: {:,}'.format(sum_val), 'websites removed from dataset')
    print ("Website problems: ")
    print ( *websites_issue_sort, sep = "\n" )
    
    print_dictionary(tiger_dict, 'Tiger no')       # TIGER fixes
    
    sum_val = sum(tiger_issue.values())
    print ('\nNumber of TIGER issues: {:,}'.format(sum_val), 'TIGER tags removed from dataset')
    print ('(TIGER is not [\'yes\', \'no\', \'aerial\'])')
    print ("TIGER problems: ")
    pp.pprint ( dict(tiger_issue) )
    
    print_dictionary(house_dict, 'House number')       # House number fixes
    
    print_dictionary(cuisine_dict, 'Cuisine name')       # Cuisine fixes
    
    total = 0
    for value in value_issue.values():
        total += len(value)
    
    print ('\nNumber of other value issues: ', total, 'tags removed from dataset')
    print ("Other value problems: ")
    pp.pprint ( dict(value_issue) )
    
    n = counts['node child key eliminated'] + counts['way child key eliminated']
    print ('\n<nodes><tags> and <ways><tags> corrupted keys: {:,}'.format(n), 'tags removed from dataset')
    print ('Tag key problems:')
    print ( *bad_keys_sort, sep = "\n" )
    
    total = sum(node_id_bad.values())
    print ('\nNumber of <nodes> eliminated: ', total, 'nodes removed from dataset')
    print ("Nodes ID problems: ")
    pp.pprint ( dict(node_id_bad) )
    
    total = sum(way_id_bad.values())
    print ('\nNumber of <ways> eliminated: ', total, 'ways removed from dataset')
    print ("Ways ID problems: ")
    pp.pprint ( dict(way_id_bad) )
    
    total = sum(way_node_reference_bad.values())
    print ('\nNumber of <ways nodes> eliminated: ', total, 'ways nodes removed from dataset')
    print ("Ways nodes reference problems: ")
    pp.pprint ( dict(way_node_reference_bad) )
    return

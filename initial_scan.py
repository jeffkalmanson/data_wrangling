# Filename: initial_scan.py
# Python 3.7
# Initial data scan to approximately size the problem data

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
from email.utils import parseaddr
from urllib.parse import urlparse
import pprint
import operator

pp = pprint.PrettyPrinter(indent=4, width=20)

map_file = 'UpperWestSideTest.osm'   # Test file size is 10.1MB

streets_issue = defaultdict(int)
us_states_issue = defaultdict(int)
cities_issue = defaultdict(int)
phones_issue = defaultdict(int)
emails_issue = defaultdict(int)
websites_issue = defaultdict(int)
zipcodes_issue = defaultdict(int)
zips_outside = defaultdict(int)
tiger_issue = defaultdict(int)
counts = defaultdict(int)

# Known correct data lists
ok_streets = [ 'Americas', 'Avenue', 'Boulevard', 'Broadway', 'Circle', 'Court', 'Drive', 'East', 'Lane',
               'North', 'Parkway', 'Place', 'Plaza', 'Road', 'South', 'Square', 'Street', 'Terrace', 'Walk',
               'Way', 'West']
ok_city = ['New York', 'New York City']
ok_domains = ['.com', '.org', '.net', '.edu', '.gov', '.us', '.nyc', '.biz', '.info', '.io', '.it',
           '.co', '.site', '.cz', '.hu', '.int']
uws_zips = ['10023', '10024', '10025']  # Upper West Side zip codes

# Regular expressions
# r prefix means raw string -- send RE module backslash -- RE module must process backslash as escape
phone_re = re.compile(r"^(\+?1?\s?-?\(?\)?)(\d{3})\D*(\d{3})\D*(\d{4})$")  # r: RE must process backslash as escape
email_re = re.compile(r"[\w.-]+@[\w.-]+")
website_re = re.compile(r"^(http\:\/\/)?(https\:\/\/)?([\w.-])*[\w-]+\.([a-zA-Z][a-zA-Z][a-zA-Z]?[a-zA-Z]?)(\/[\w/.#?=%&,!+()-]*)?$")
street_re = re.compile(r"\b\S+\.?$", re.IGNORECASE)

def count_issues_states(name):
    """If state is not NY, record the problem and return None.
    
    Arguments:
    name -- the value of the addr:state key
    """
    if not name or name != 'NY':
        us_states_issue[name] += 1
        return

def count_issues_cities(name):
    """If city is not in list, record the problem and return None.
    
    Arguments:
    name -- the value of the addr:city key
    """
    if not name or name not in ok_city:
        cities_issue[name] += 1
        return

def count_issues_phones(name):
    """If phone number is a dud or does not fit pattern, record the problem and return None.
    
    Arguments:
    name -- the value of the phone key
    """
    if not name or name.isspace():
        phones_issue[name] += 1
        return
    
    match = phone_re.search(name)
    if not match:
        phones_issue[name] += 1
        return

def count_issues_emails(name):
    """If email is a dud or does not parse, record the problem and return None.
    
    Arguments:
    name -- the value of the email key
    """
    if not name or name.isspace():
        emails_issue[name] += 1
        return
    
    name = name.lower()
    first_parse = parseaddr(name)
    second_parse = not email_re.search(name)
    third_parse = not first_parse[1].endswith(tuple(ok_domains))
    
    if first_parse == ('', '') or second_parse or third_parse:
        emails_issue[name] += 1
        return
    
def count_issues_websites(name):
    """If website is a dud or does not parse, record the problem and return None.
    
    Arguments:
    name -- the value of the website or url key
    """
    if not name or name.isspace():
        websites_issue[name] += 1
        return
    
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
        return

def count_issues_zipcodes(name):
    """If zip code is a dud or does not parse, record the problem and return None.
    
    Arguments:
    name -- the value of the addr:postcode key
    """
    if not name or name.isspace():
        zipcodes_issue[name] += 1
        return

    if (not name.isdigit()) or len(name) != 5:
        zipcodes_issue[name] += 1
        return
    
    if name not in uws_zips:
        zips_outside[name] += 1
        return

def count_issues_tiger(name):
    """If TIGER is a dud or not in list, record the problem and return None.
    
    Arguments:
    name -- the value of the tiger:reviewed key
    """
    if not name or name.isspace():
        tiger_issue[name] += 1
        return
    
    if name not in ['yes', 'no']:
        tiger_issue[name] += 1
        return

def count_issues_streets(name):
    """If street is a dud or does not parse, record the problem and return None.
    
    Arguments:
    name -- the value of the addr:street key
    """
    if not name or name.isspace():
        streets_issue[name] += 1
        return
    
    m = street_re.search(name)
    if m:
        street_type = m.group()          # returns a String
        if street_type not in ok_streets:
            streets_issue[street_type] += 1
            return

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
    return (elem.tag == "tag") and (elem.attrib["k"] == "website" or (elem.attrib["k"] == "url"))

def is_zipcode(elem):
    """Examine the key of the element tag and return a boolean.
    
    Arguments:
    elem -- the current XML element in the Element Tree iteration
    """
    return (elem.tag == "tag") and (elem.attrib["k"] == "addr:postcode")

def is_tiger(elem):
    """Examine the key of the element tag and return a boolean.
    
    Arguments:
    elem -- the current XML element in the Element Tree iteration
    """
    return (elem.tag == "tag") and (elem.attrib["k"] == "tiger:reviewed")


def initialize_dicts():
    """Flush the toilet and return a boolean."""
    try:
        streets_issue.clear()
        us_states_issue.clear()
        cities_issue.clear()
        phones_issue.clear()
        emails_issue.clear()
        websites_issue.clear()
        zipcodes_issue.clear()
        zips_outside.clear()
        tiger_issue.clear()
        counts.clear()
    except:
        return None
    
    return True

#----------------------#
#     Main routine     #
#----------------------#

def initial_count_problems():
    """Count the dataset and the problem data, print a report, and return None."""
    response = initialize_dicts()
    
    if not response:
        print ('Fatal Error initializing dictionaries')
        print ('\nTerminating execution...')
        return None
    
    osm_file = open(map_file, "r")
    
    for event, elem in ET.iterparse(osm_file):
        if event == "end":
            if is_street(elem):
                counts['total_street'] += 1
                count_issues_streets(elem.attrib['v'])
            
            if is_city(elem):
                counts['total_city'] += 1
                count_issues_cities(elem.attrib["v"])
                
            if is_state(elem):
                counts['total_state'] += 1
                count_issues_states(elem.attrib["v"])
            
            if is_zipcode(elem):
                counts['total_zipcode'] += 1
                count_issues_zipcodes(elem.attrib["v"])
            
            if is_phone(elem):
                counts['total_phone'] += 1
                count_issues_phones(elem.attrib["v"])
                
            if is_email(elem):
                counts['total_email'] += 1
                count_issues_emails(elem.attrib["v"])
                
            if is_website(elem):
                counts['total_website'] += 1
                count_issues_websites(elem.attrib["v"])
            
            if is_tiger(elem):
                counts['total_tiger'] += 1
                count_issues_tiger(elem.attrib["v"])
        
        counts['record_count'] += 1         
        elem.clear()
    
    osm_file.close()
    print_initial_scan()
    return

def print_initial_scan():
    """Print a report and return None."""
    streets_issue_sort = sorted(streets_issue.items(), key=operator.itemgetter(1))
    streets_issue_sort.reverse()  # Note: In-place reversal
    
    cities_issue_sort = sorted(cities_issue.items(), key=operator.itemgetter(1))
    cities_issue_sort.reverse()  # Note: In-place reversal
    
    us_states_issue_sort = sorted(us_states_issue.items(), key=operator.itemgetter(1))
    us_states_issue_sort.reverse()  # Note: In-place reversal
    
    zipcodes_issue_sort = sorted(zipcodes_issue.items(), key=operator.itemgetter(1))
    zipcodes_issue_sort.reverse()  # Note: In-place reversal
    
    zips_outside_sort = sorted(zips_outside.items(), key=operator.itemgetter(1))
    zips_outside_sort.reverse()  # Note: In-place reversal
    
    phones_issue_sort = sorted(phones_issue.items(), key=operator.itemgetter(1))
    phones_issue_sort.reverse()  # Note: In-place reversal
    
    emails_issue_sort = sorted(emails_issue.items(), key=operator.itemgetter(1))
    emails_issue_sort.reverse()  # Note: In-place reversal
    
    websites_issue_sort = sorted(websites_issue.items(), key=operator.itemgetter(1))
    websites_issue_sort.reverse()  # Note: In-place reversal
    
    sum_val = sum(streets_issue.values())
    print ('Number of street issues: {:,}'.format(sum_val))
    print ('Total number of streets: {:,}'.format(counts['total_street']),           \
           '  Percent problems: {:.1%}'.format(float(sum_val)/counts['total_street']))
    print ("Street problems: ")
    print ( *streets_issue_sort, sep = "\n" )
    
    sum_val = sum(cities_issue.values())
    print ('\nNumber of city issues: {:,}'.format(sum_val))
    print ('Total number of cities: {:,}'.format(counts['total_city']),            \
           '  Percent problems: {:.1%}'.format(float(sum_val)/counts['total_city']))
    print ("City problems: ")
    print ( *cities_issue_sort, sep = "\n" )
    
    sum_val = sum(us_states_issue.values())
    print ('\nNumber of state issues: {:,}'.format(sum_val))
    print ('Total number of states: {:,}'.format(counts['total_state']),            \
           '  Percent problems: {:.1%}'.format(float(sum_val)/counts['total_state']))
    print ("State problems: ")
    print ( *us_states_issue_sort, sep = "\n" )
    
    sum_val = sum(zipcodes_issue.values())
    print ('\nNumber of zipcode issues: {:,}'.format(sum_val))
    print ('Total number of zipcodes: {:,}'.format(counts['total_zipcode']),          \
           '  Percent problems: {:.1%}'.format(float(sum_val)/counts['total_zipcode']))
    print ("Zip code problems: ")
    print ( *zipcodes_issue_sort, sep = "\n" )
    
    sum_val = sum(zips_outside.values())
    print ('\nNumber of zipcodes outside Upper West Side: {:,}'.format(sum_val))
    print ('Total number of zipcodes: {:,}'.format(counts['total_zipcode']),             \
           '  Percent outside UWS: {:.1%}'.format(float(sum_val)/counts['total_zipcode']))
    print ("Zip codes outside UWS: ")
    print ( *zips_outside_sort, sep = "\n" )
    
    sum_val = sum(phones_issue.values())
    print ('\nNumber of phone number issues: {:,}'.format(sum_val))
    print ('Total number of phone numbers: {:,}'.format(counts['total_phone']),     \
           '  Percent problems: {:.1%}'.format(float(sum_val)/counts['total_phone']))
    print ("Phone problems: ")
    print ( *phones_issue_sort, sep = "\n" )
    
    sum_val = sum(emails_issue.values())
    print ('\nNumber of email address issues: {:,}'.format(sum_val))
    print ('Total number of email addresses: {:,}'.format(counts['total_email']),   \
           '  Percent problems: {:.1%}'.format(float(sum_val)/counts['total_email']))
    print ("email problems: ")
    print ( *emails_issue_sort, sep = "\n" )
    
    sum_val = sum(websites_issue.values())
    print ('\nNumber of website URL issues: {:,}'.format(sum_val))
    print ('Total number of websites: {:,}'.format(counts['total_website']),          \
           '  Percent problems: {:.1%}'.format(float(sum_val)/counts['total_website']))
    print ("Website problems: ")
    print ( *websites_issue_sort, sep = "\n" )
    
    sum_val = sum(tiger_issue.values())
    print ('\nNumber of TIGER issues: {:,}'.format(sum_val))
    print ('Total number of TIGER: {:,}'.format(counts['total_tiger']),             \
           '  Percent problems: {:.1%}'.format(float(sum_val)/counts['total_tiger']))
    print ("TIGER problems: ")
    pp.pprint ( dict(tiger_issue) )
    
    print ( "\nTotal record count: {:,}".format(counts['record_count']) )
    return

if __name__ == '__main__':
    initial_count_problems()
